const DEVICE_STATES = new Set([
  'playing',
  'paused',
  'buffering',
  'on',
  'idle',
  'off',
  'unknown',
  'unavailable',
]);

const APP_ALIASES = new Map([
  ['plex', 'Plex'],
  ['com.plexapp.android', 'Plex'],
  ['com.plexapp.mediaserver.smb', 'Plex'],
  ['emby', 'Emby'],
  ['tv.emby.embyatv', 'Emby'],
  ['com.mb.android', 'Emby'],
  ['silo', 'Silo'],
  ['tivimate', 'TiviMate'],
  ['ar.tvplayer.tv', 'TiviMate'],
]);

const STATUS_LABELS = {
  playing: 'Playing',
  paused: 'Paused',
  buffering: 'Buffering',
  app: 'App open',
  on: 'On',
  idle: 'Idle',
  off: 'Off',
  unknown: 'Unknown',
  unavailable: 'Unavailable',
};

const ACTIVE_STATUSES = new Set(['playing', 'paused', 'buffering', 'app', 'on']);
const METADATA_PROVENANCE = Symbol('metadata-provenance');

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function safeImageUrl(value) {
  if (typeof value !== 'string' || value.length === 0 || value !== value.trim()) return null;
  if (/[\u0000-\u0020\\]/.test(value)) return null;
  if (value.startsWith('/') && !value.startsWith('//')) return value;
  if (!/^https?:\/\//i.test(value)) return null;

  try {
    const parsed = new URL(value);
    if (!['http:', 'https:'].includes(parsed.protocol) || !parsed.hostname) return null;
    if (parsed.username || parsed.password) return null;
    return value;
  } catch {
    return null;
  }
}

function nonEmptyString(value, field, { optional = false } = {}) {
  if (optional && value === undefined) return undefined;
  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new TypeError(`${field} must be a non-empty string`);
  }
  return value.trim();
}

function appKey(value) {
  return value.trim().toLowerCase().replace(/\s+/g, ' ');
}

/** Validate and normalize the card's public configuration. */
export function normalizeConfig(config) {
  if (!isRecord(config)) throw new TypeError('Configuration must be an object');
  const allowedConfigKeys = new Set(['type', 'devices', 'app_logos', 'grid_options', 'visibility']);
  for (const key of Object.keys(config)) {
    if (!allowedConfigKeys.has(key)) throw new TypeError(`Unknown configuration field: ${key}`);
  }
  if (config.type !== undefined && config.type !== 'custom:nmd-media-card') {
    throw new TypeError("type must be 'custom:nmd-media-card'");
  }
  if (config.grid_options !== undefined && !isRecord(config.grid_options)) {
    throw new TypeError('grid_options must be an object');
  }
  if (config.visibility !== undefined && !isRecord(config.visibility) && !Array.isArray(config.visibility)) {
    throw new TypeError('visibility must be an object or array');
  }
  if (!Array.isArray(config.devices) || config.devices.length === 0) {
    throw new TypeError('devices must be a non-empty array');
  }

  const ids = new Set();
  const devices = config.devices.map((input, index) => {
    let source;
    if (typeof input === 'string') source = { entity: input };
    else if (isRecord(input)) source = input;
    else throw new TypeError(`devices[${index}] must be an entity ID or object`);

    for (const key of Object.keys(source)) {
      if (!['entity', 'name', 'state_source', 'app_name'].includes(key)) {
        throw new TypeError(`Unknown device field: ${key}`);
      }
    }

    const entity = nonEmptyString(source.entity, `devices[${index}].entity`);
    if (!/^media_player\.[a-z0-9_]+$/.test(entity)) {
      throw new TypeError(`devices[${index}].entity must be a media_player entity ID`);
    }
    if (ids.has(entity)) throw new TypeError(`Duplicate media player entity: ${entity}`);
    ids.add(entity);

    const stateSource = source.state_source ?? 'entity';
    if (!['entity', 'app'].includes(stateSource)) {
      throw new TypeError(`devices[${index}].state_source must be 'entity' or 'app'`);
    }

    const device = { entity, state_source: stateSource };
    if (source.name !== undefined) device.name = nonEmptyString(source.name, `devices[${index}].name`);
    if (source.app_name !== undefined) {
      device.app_name = nonEmptyString(source.app_name, `devices[${index}].app_name`);
    }
    return device;
  });

  const logos = config.app_logos === undefined ? {} : config.app_logos;
  if (!isRecord(logos)) throw new TypeError('app_logos must be an object');
  const app_logos = {};
  for (const [key, url] of Object.entries(logos)) {
    const name = nonEmptyString(key, 'app_logos key');
    const normalizedUrl = safeImageUrl(url);
    if (!normalizedUrl) throw new TypeError(`app_logos.${key} must be a safe HTTP(S) or root-relative URL`);
    Object.defineProperty(app_logos, appKey(name), {
      value: normalizedUrl,
      enumerable: true,
      configurable: true,
      writable: true,
    });
  }

  return { devices, app_logos };
}

function finiteNumber(value) {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim() !== '') {
    const number = Number(value);
    if (Number.isFinite(number)) return number;
  }
  return null;
}

function supported(features, bit) {
  const value = finiteNumber(features);
  return value !== null && value >= 0 && Math.floor(value) === value && (value & bit) === bit;
}

function knownApp(value) {
  if (typeof value !== 'string' || value.trim() === '') return null;
  const normalized = appKey(value);
  const match = APP_ALIASES.get(normalized);
  if (match) return { name: match, key: appKey(match) };
  return { name: value.trim(), key: normalized };
}

function identifyApp(device, attributes, platform) {
  for (const reported of [attributes.app_name, attributes.app_id]) {
    if (typeof reported === 'string' && reported.trim()) return knownApp(reported);
  }
  if (typeof platform === 'string' && platform.trim()) {
    const known = APP_ALIASES.get(appKey(platform));
    if (known) return { name: known, key: appKey(known) };
  }
  return typeof device?.app_name === 'string' ? knownApp(device.app_name) : null;
}

function rawMetadata(attributes) {
  return [
    attributes.media_title ?? null,
    attributes.media_content_id ?? null,
    attributes.media_series_title ?? null,
    attributes.media_season ?? null,
    attributes.media_episode ?? null,
    attributes.media_episode_title ?? null,
    attributes.media_channel ?? null,
    attributes.media_artist ?? null,
    attributes.media_album_name ?? null,
  ];
}

function signatureOf(value) {
  // Keep raw item identifiers and signed artwork URLs out of stored signatures.
  const text = JSON.stringify(value);
  let first = 0x811c9dc5;
  let second = 0x9e3779b9;
  for (let index = 0; index < text.length; index += 1) {
    const code = text.charCodeAt(index);
    first = Math.imul(first ^ code, 0x01000193);
    second = Math.imul(second ^ code, 0x85ebca6b);
  }
  return `${(first >>> 0).toString(16).padStart(8, '0')}${(second >>> 0).toString(16).padStart(8, '0')}`;
}

function metadataDetail(attributes) {
  const series = attributes.media_series_title;
  const season = finiteNumber(attributes.media_season);
  const episode = finiteNumber(attributes.media_episode);
  if (typeof series === 'string' && series.trim()) {
    const episodeTitle = typeof attributes.media_episode_title === 'string' && attributes.media_episode_title.trim()
      ? attributes.media_episode_title.trim()
      : attributes.media_title;
    const distinctEpisodeTitle = typeof episodeTitle === 'string' && episodeTitle.trim()
      && episodeTitle.trim().toLowerCase() !== series.trim().toLowerCase()
      ? episodeTitle.trim()
      : null;
    const episodeParts = [];
    if (season !== null && season >= 0) episodeParts.push(`S${Math.floor(season)}`);
    if (episode !== null && episode >= 0) episodeParts.push(`E${Math.floor(episode)}`);
    const episodeCode = episodeParts.join(' · ');
    if (episodeCode && distinctEpisodeTitle) return `${episodeCode} — ${distinctEpisodeTitle}`;
    if (episodeCode) return episodeCode;
    if (distinctEpisodeTitle) return distinctEpisodeTitle;
    return null;
  }

  const channel = attributes.media_channel;
  if (typeof channel === 'string' && channel.trim()) return channel.trim();
  const artist = attributes.media_artist;
  const album = attributes.media_album_name;
  if (typeof artist === 'string' && artist.trim()) {
    return typeof album === 'string' && album.trim() ? `${artist.trim()} · ${album.trim()}` : artist.trim();
  }
  return null;
}

function progressFor(attributes, state, now) {
  const duration = finiteNumber(attributes.media_duration);
  let position = finiteNumber(attributes.media_position);
  if (duration === null || duration <= 0 || position === null || position < 0) return null;

  const updatedAt = typeof attributes.media_position_updated_at === 'string'
    ? Date.parse(attributes.media_position_updated_at)
    : NaN;
  const currentTime = finiteNumber(now);
  if (state === 'playing' && Number.isFinite(updatedAt) && currentTime !== null && updatedAt <= currentTime) {
    position += (currentTime - updatedAt) / 1000;
  }
  position = Math.min(duration, Math.max(0, position));
  return {
    position,
    duration,
    percent: Math.min(100, Math.max(0, (position / duration) * 100)),
  };
}

function baseResult(device, entity, status) {
  const attributes = isRecord(entity?.attributes) ? entity.attributes : {};
  const entityId = device?.entity ?? entity?.entity_id ?? '';
  const name = device?.name ?? attributes.friendly_name ?? entityId;
  return {
    entity: entityId,
    name,
    status,
    statusLabel: STATUS_LABELS[status],
    active: ACTIVE_STATUSES.has(status),
    appName: null,
    appKey: null,
    appIdentity: null,
    title: null,
    titleIsAppFallback: false,
    detail: null,
    artwork: null,
    progress: null,
    action: null,
    metadataSignature: signatureOf(rawMetadata(attributes)),
    metadataStale: false,
  };
}

/** Convert one configured device and its Home Assistant entity to display data. */
export function buildDevice(device, entity, { now = Date.now(), previous = null, platform = null } = {}) {
  // History belongs to one configured entity, even if a caller supplies another
  // room's previous model.
  if (previous?.entity !== (device?.entity ?? entity?.entity_id ?? '')) previous = null;
  const rawState = typeof entity?.state === 'string' ? entity.state.toLowerCase() : null;
  if (!entity || typeof entity !== 'object') {
    const missing = baseResult(device, null, 'unavailable');
    if (previous) {
      missing.appIdentity = previous.appIdentity ?? null;
      missing.metadataSignature = previous.metadataSignature ?? missing.metadataSignature;
      missing.metadataStale = Boolean(previous.metadataStale);
      if (previous[METADATA_PROVENANCE]) {
        Object.defineProperty(missing, METADATA_PROVENANCE, { value: previous[METADATA_PROVENANCE] });
      }
    }
    return missing;
  }

  let state = DEVICE_STATES.has(rawState) ? rawState : 'unknown';
  if (rawState === null || rawState === '') state = 'unknown';
  const result = baseResult(device, entity, state);
  const attributes = isRecord(entity.attributes) ? entity.attributes : {};
  const app = identifyApp(device, attributes, platform);
  const identity = app?.key ?? previous?.appIdentity ?? null;
  const signature = result.metadataSignature;
  const inactive = state === 'unknown' || state === 'unavailable' || state === 'off' || state === 'idle';
  const history = previous?.[METADATA_PROVENANCE];
  let programme = history?.programme ?? null;
  let artwork = history?.artwork ?? null;
  const hasMetadata = rawMetadata(attributes).some(value =>
    typeof value === 'string' ? Boolean(value.trim()) : value !== null);
  const picture = safeImageUrl(attributes.entity_picture);
  const pictureSignature = picture ? signatureOf(picture) : null;

  // Empty snapshots cannot erase the last meaningful source. Progress and
  // artwork refreshes cannot establish that programme fields belong to a new app.
  const programmeFromOtherApp = Boolean(programme?.appIdentity && identity && programme.appIdentity !== identity);
  const artworkFromOtherApp = Boolean(artwork?.appIdentity && identity && artwork.appIdentity !== identity);
  result.appIdentity = identity;
  result.metadataStale = programmeFromOtherApp && (!hasMetadata || signature === programme.signature);
  const artworkStale = artworkFromOtherApp && pictureSignature === artwork.signature;
  // Attribute initial/same-app inactive data too: HA may first publish retained
  // fields while idle. Never transfer existing ownership to a different idle app.
  if (hasMetadata && !result.metadataStale && (!inactive || !programme || programme.appIdentity === identity)) {
    programme = { appIdentity: identity, signature };
  }
  if (picture && !artworkStale && (!inactive || !artwork || artwork.appIdentity === identity)) {
    artwork = { appIdentity: identity, signature: pictureSignature };
  }
  Object.defineProperty(result, METADATA_PROVENANCE, { value: { programme, artwork } });

  // Keep source history across idle/off transitions, but
  // never expose an app label or old media details in those states.
  if (inactive) return result;

  if (app) {
    result.appName = app.name;
    result.appKey = app.key;
  }

  const assumed = device?.state_source === 'app'
    || appKey(typeof platform === 'string' ? platform : '') === 'androidtv_remote'
    || attributes.assumed_state === true;

  if (assumed || state === 'on') {
    if (app) {
      result.status = 'app';
      result.statusLabel = STATUS_LABELS.app;
      result.active = true;
      result.title = app.name;
      result.titleIsAppFallback = true;
      result.detail = app.key === 'tivimate'
        ? 'Channel information unavailable'
        : 'Programme information unavailable';
    } else {
      result.status = 'on';
      result.statusLabel = STATUS_LABELS.on;
      result.active = true;
      result.title = 'Media player on';
      result.detail = assumed ? 'Playback not confirmed' : null;
    }
    return result;
  }

  const metadataStale = result.metadataStale;

  const candidateTitle = typeof attributes.media_series_title === 'string' && attributes.media_series_title.trim()
    ? attributes.media_series_title
    : attributes.media_title;
  const detail = metadataDetail(attributes);
  const hasTitle = typeof candidateTitle === 'string' && Boolean(candidateTitle.trim());
  if (state === 'playing' || state === 'paused' || state === 'buffering' || state === 'on') {
    result.titleIsAppFallback = !metadataStale && !hasTitle && Boolean(app);
    result.title = metadataStale ? (state === 'on' ? (device?.name ?? 'Media player on') : 'Media playing')
      : (typeof candidateTitle === 'string' && candidateTitle.trim()
        ? candidateTitle.trim()
        : (app?.name ?? (state === 'on' ? (device?.name ?? 'Media player on') : 'Media playing')));
    result.detail = metadataStale ? 'Programme information unavailable'
      : (detail ?? 'Programme information unavailable');
    result.artwork = artworkStale ? null : picture;
    result.progress = metadataStale ? null : progressFor(attributes, state, now);
  }
  if (state === 'playing' && supported(attributes.supported_features, 1)) result.action = 'media_pause';
  if (state === 'paused' && supported(attributes.supported_features, 16384)) result.action = 'media_play';

  // The signature intentionally describes metadata only; advancing playback
  // position must not make old app metadata look fresh.
  return result;
}

/** Keep the current active room selected, otherwise choose the strongest state. */
export function chooseFeatured(devices, selectedId) {
  if (!Array.isArray(devices) || devices.length === 0) return null;
  const selected = devices.find((device) => device?.entity === selectedId);
  if (selected?.active) return selected;

  const priorities = ['playing', 'paused', 'buffering', 'app', 'on'];
  for (const status of priorities) {
    const active = devices.find((device) => device?.status === status);
    if (active) return active;
  }
  return null;
}

/** Format a non-negative duration as m:ss or h:mm:ss. */
export function formatTime(seconds) {
  const value = finiteNumber(seconds);
  if (value === null || value < 0) return '–:––';
  const total = Math.floor(value);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const remainder = total % 60;
  if (hours > 0) return `${hours}:${String(minutes).padStart(2, '0')}:${String(remainder).padStart(2, '0')}`;
  return `${minutes}:${String(remainder).padStart(2, '0')}`;
}
