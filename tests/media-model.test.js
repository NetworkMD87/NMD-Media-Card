import test from 'node:test';
import assert from 'node:assert/strict';

import {
  buildDevice,
  chooseFeatured,
  formatTime,
  normalizeConfig,
  safeImageUrl,
} from '../src/media-model.js';

const configured = (entity = 'media_player.den') => ({ entity, name: 'Den Shield' });
const stateEntity = (state, attributes = {}) => ({ state, attributes });

test('normalizes string and object devices and lower-cases app logo keys', () => {
  assert.deepEqual(normalizeConfig({
    devices: ['media_player.den', { entity: 'media_player.study', name: 'Study', app_name: 'TiviMate' }],
    app_logos: { Plex: '/local/plex.svg', TiviMate: 'https://assets.example/tivimate.svg' },
  }), {
    devices: [
      { entity: 'media_player.den', state_source: 'entity' },
      { entity: 'media_player.study', state_source: 'entity', name: 'Study', app_name: 'TiviMate' },
    ],
    app_logos: { plex: '/local/plex.svg', tivimate: 'https://assets.example/tivimate.svg' },
  });
});

test('accepts a standard Home Assistant card configuration', () => {
  assert.deepEqual(normalizeConfig({
    type: 'custom:nmd-media-card',
    grid_options: { columns: 6, rows: 2 },
    visibility: [{ condition: 'user', users: ['user-id'] }],
    devices: [{ entity: 'media_player.den', name: 'Den' }],
    app_logos: { plex: '/local/plex.svg' },
  }), {
    devices: [{ entity: 'media_player.den', state_source: 'entity', name: 'Den' }],
    app_logos: { plex: '/local/plex.svg' },
  });
  assert.throws(() => normalizeConfig({ type: 'custom:other-card', devices: ['media_player.den'] }));
});

test('rejects malformed, duplicate and unsafe configuration', () => {
  for (const config of [
    null,
    {},
    { devices: [] },
    { devices: ['sensor.tv'] },
    { devices: ['media_player.Den'] },
    { devices: ['media_player.den', 'media_player.den'] },
    { devices: [{ entity: 'media_player.den', state_source: 'guess' }] },
    { devices: ['media_player.den'], extra: true },
    { devices: ['media_player.den'], app_logos: null },
    { devices: ['media_player.den'], app_logos: { plex: 'data:image/svg+xml,hi' } },
    { devices: ['media_player.den'], app_logos: { plex: 'javascript:alert(1)' } },
    { devices: ['media_player.den'], app_logos: { plex: 'https://user:pass@example.test/logo.png' } },
    { devices: [{ entity: 'media_player.den', app_logo: '/logo.svg' }] },
  ]) assert.throws(() => normalizeConfig(config));
});

test('allows only HTTP(S) and single-root-relative image URLs', () => {
  assert.equal(safeImageUrl('/api/media_player_proxy/media_player.den'), '/api/media_player_proxy/media_player.den');
  assert.equal(safeImageUrl('https://cdn.example/image.jpg'), 'https://cdn.example/image.jpg');
  for (const url of [
    '//cdn.example/image.jpg',
    'data:image/png;base64,AA==',
    'javascript:alert(1)',
    'https://user:secret@cdn.example/image.jpg',
    'https://cdn.example/a b.jpg',
  ]) assert.equal(safeImageUrl(url), null);
});

test('preserves each reported state, active flag and status label', () => {
  const states = [
    ['playing', true, 'Playing'], ['paused', true, 'Paused'], ['buffering', true, 'Buffering'],
    ['on', true, 'On'], ['idle', false, 'Idle'], ['off', false, 'Off'],
    ['unknown', false, 'Unknown'], ['unavailable', false, 'Unavailable'], ['invalid', false, 'Unknown'],
  ];
  for (const [state, active, label] of states) {
    const model = buildDevice(configured(), stateEntity(state));
    assert.equal(model.status, state === 'invalid' ? 'unknown' : state);
    assert.equal(model.active, active);
    assert.equal(model.statusLabel, label);
  }
  assert.equal(buildDevice(configured(), null).status, 'unavailable');
});

test('clears stale media details in idle, off and unavailable states', () => {
  for (const state of ['idle', 'off', 'unavailable', 'unknown']) {
    const result = buildDevice(configured(), stateEntity(state, {
      media_title: 'Old programme',
      media_position: 40,
      media_duration: 100,
      entity_picture: '/old.jpg',
      app_name: 'Plex',
    }));
    assert.equal(result.title, null);
    assert.equal(result.artwork, null);
    assert.equal(result.progress, null);
    assert.equal(result.appName, null);
  }
});

test('shows active media title, episode and channel details with safe artwork', () => {
  const tv = buildDevice(configured(), stateEntity('playing', {
    media_title: 'The Episode',
    media_series_title: 'A Series',
    media_season: 2,
    media_episode: 4,
    media_episode_title: 'The Episode',
    entity_picture: 'https://media.example/poster.jpg',
    supported_features: 1,
  }));
  assert.equal(tv.title, 'A Series');
  assert.equal(tv.detail, 'S2 · E4 — The Episode');
  assert.equal(tv.artwork, 'https://media.example/poster.jpg');
  assert.equal(tv.action, 'media_pause');

  const live = buildDevice(configured(), stateEntity('playing', { media_channel: 'BBC One' }));
  assert.equal(live.detail, 'BBC One');
  assert.equal(live.title, 'Media playing');
  assert.equal(live.artwork, null);

  const sourceOnly = buildDevice(configured(), stateEntity('playing', { source: 'BBC One' }));
  assert.equal(sourceOnly.detail, 'Programme information unavailable');
});

test('Silo with a current title omits missing programme details without losing playback data', () => {
  for (const state of ['playing', 'paused']) {
    const attrs = { app_name: 'Silo', media_title: 'Shelby Oaks', media_position: 1814,
      media_duration: 5452, supported_features: 16385 };
    const result = buildDevice(configured(), stateEntity(state, attrs));
    assert.equal(result.title, 'Shelby Oaks');
    assert.equal(result.detail, null);
    assert.equal(result.artwork, null);
    assert.ok(result.progress);
    assert.equal(result.action, state === 'playing' ? 'media_pause' : 'media_play');
    assert.equal(buildDevice(configured(), stateEntity(state, { ...attrs, media_channel: 'Channel' })).detail, 'Channel');
    assert.equal(buildDevice(configured(), stateEntity(state, { ...attrs, media_title: '' })).detail, 'Programme information unavailable');
    const previous = buildDevice(configured(), stateEntity(state, { ...attrs, app_name: 'Plex' }));
    assert.equal(previous.detail, 'Programme information unavailable');
    assert.equal(buildDevice(configured(), stateEntity(state, attrs), { previous }).detail, 'Programme information unavailable');
  }
});

test('treats on as unknown playback and never carries programme metadata forward', () => {
  const attrs = {
    app_name: 'TiviMate',
    media_title: 'Old programme',
    media_channel: 'BBC One',
    media_position: 22,
    media_duration: 100,
    entity_picture: '/old.jpg',
    supported_features: 16385,
  };
  const app = buildDevice(configured(), stateEntity('on', attrs));
  assert.equal(app.status, 'app');
  assert.equal(app.title, 'TiviMate');
  assert.equal(app.detail, 'Channel information unavailable');
  assert.equal(app.artwork, null);
  assert.equal(app.progress, null);
  assert.equal(app.action, null);

  const online = buildDevice(configured(), stateEntity('on', { ...attrs, app_name: undefined, app_id: undefined }));
  assert.equal(online.status, 'on');
  assert.equal(online.title, 'Media player on');
  assert.equal(online.artwork, null);
  assert.equal(online.progress, null);
  assert.equal(online.action, null);
});

test('offers controls only when the state and feature bit support them', () => {
  assert.equal(buildDevice(configured(), stateEntity('playing', { supported_features: 1 })).action, 'media_pause');
  assert.equal(buildDevice(configured(), stateEntity('paused', { supported_features: 16384 })).action, 'media_play');
  for (const features of [0, 2, undefined, -1, 'not-a-number']) {
    assert.equal(buildDevice(configured(), stateEntity('playing', { supported_features: features })).action, null);
    assert.equal(buildDevice(configured(), stateEntity('paused', { supported_features: features })).action, null);
  }
  assert.equal(buildDevice(configured(), stateEntity('buffering', { supported_features: 1 })).action, null);
});

test('advances only valid playing progress and clamps it to the duration', () => {
  const now = Date.parse('2026-10-07T10:00:10Z');
  assert.deepEqual(buildDevice(configured(), stateEntity('playing', {
    media_position: 20,
    media_duration: 100,
    media_position_updated_at: '2026-10-07T10:00:00Z',
  }), { now }).progress, { position: 30, duration: 100, percent: 30 });

  assert.deepEqual(buildDevice(configured(), stateEntity('paused', {
    media_position: 20,
    media_duration: 100,
    media_position_updated_at: '2026-10-07T10:00:00Z',
  }), { now }).progress, { position: 20, duration: 100, percent: 20 });

  assert.equal(buildDevice(configured(), stateEntity('playing', {
    media_position: 110,
    media_duration: 100,
    media_position_updated_at: '2026-10-07T10:01:00Z',
  }), { now }).progress.position, 100);
  for (const attrs of [
    { media_position: -1, media_duration: 100 },
    { media_position: 1, media_duration: 0 },
    { media_position: 'bad', media_duration: 100 },
  ]) assert.equal(buildDevice(configured(), stateEntity('playing', attrs)).progress, null);
});

test('treats app-only, Android TV Remote and assumed states as unconfirmed playback', () => {
  const raw = stateEntity('playing', {
    app_id: 'ar.tvplayer.tv',
    media_title: 'Stale title',
    media_position: 45,
    media_duration: 100,
    entity_picture: '/stale.jpg',
    supported_features: 16385,
  });

  for (const [device, options] of [
    [{ ...configured(), state_source: 'app' }, {}],
    [configured(), { platform: 'androidtv_remote' }],
    [configured(), {}],
  ]) {
    const entity = options.platform ? raw : (device.state_source === 'app'
      ? raw
      : stateEntity('playing', { ...raw.attributes, assumed_state: true }));
    const result = buildDevice(device, entity, options);
    assert.equal(result.status, 'app');
    assert.equal(result.statusLabel, 'App open');
    assert.equal(result.title, 'TiviMate');
    assert.equal(result.detail, 'Channel information unavailable');
    assert.equal(result.artwork, null);
    assert.equal(result.progress, null);
    assert.equal(result.action, null);
  }

  const assumed = buildDevice(configured(), stateEntity('paused', {
    app_name: 'Plex', assumed_state: true, media_title: 'Old',
  }));
  assert.equal(assumed.status, 'app');
  assert.equal(assumed.title, 'Plex');
  assert.equal(assumed.detail, 'Programme information unavailable');
  assert.equal(assumed.action, null);

  const idle = buildDevice(configured(), stateEntity('idle', { app_name: 'Plex' }), { platform: 'androidtv_remote' });
  assert.equal(idle.status, 'idle');
  assert.equal(idle.title, null);
});

test('falls back conservatively to known platforms and configured app name', () => {
  const platformApp = buildDevice(configured(), stateEntity('playing'), { platform: 'emby' });
  assert.equal(platformApp.appName, 'Emby');
  const configuredApp = buildDevice({ ...configured(), app_name: 'Local Player' }, stateEntity('playing'));
  assert.equal(configuredApp.appName, 'Local Player');
  assert.equal(configuredApp.title, 'Local Player');
});

test('falls back from a blank app_name to app_id', () => {
  const result = buildDevice(configured(), stateEntity('playing', {
    app_name: '  ', app_id: 'ar.tvplayer.tv',
  }));
  assert.equal(result.appName, 'TiviMate');
  assert.equal(result.appKey, 'tivimate');
});

test('includes media_content_id in signatures but ignores arbitrary source', () => {
  const first = buildDevice(configured(), stateEntity('playing', {
    media_title: 'Same title', media_content_id: 'item-1', source: 'old-source',
  }));
  const sameItem = buildDevice(configured(), stateEntity('playing', {
    media_title: 'Same title', media_content_id: 'item-1', source: 'new-source',
  }));
  const differentItem = buildDevice(configured(), stateEntity('playing', {
    media_title: 'Same title', media_content_id: 'item-2', source: 'old-source',
  }));
  assert.equal(first.metadataSignature, sameItem.metadataSignature);
  assert.notEqual(first.metadataSignature, differentItem.metadataSignature);
});

test('suppresses unchanged metadata after an app switch until metadata changes', () => {
  const attrs = {
    app_name: 'Plex',
    media_title: 'Old title',
    media_series_title: 'Old series',
    media_content_id: 'plex-item-1',
    entity_picture: '/old.jpg',
    media_position: 15,
    media_duration: 90,
  };
  const first = buildDevice(configured(), stateEntity('playing', attrs));
  const switched = buildDevice(configured(), stateEntity('playing', { ...attrs, app_name: 'Emby' }), { previous: first });
  assert.equal(switched.metadataStale, true);
  assert.equal(switched.metadataSignature, first.metadataSignature);
  assert.equal(switched.title, 'Media playing');
  assert.equal(switched.artwork, null);
  assert.equal(switched.progress, null);

  const persistent = buildDevice(configured(), stateEntity('playing', { ...attrs, app_name: 'Emby' }), { previous: switched });
  assert.equal(persistent.metadataStale, true);

  const fresh = buildDevice(configured(), stateEntity('playing', {
    ...attrs, app_name: 'Emby', media_title: 'New title', media_series_title: 'New series',
    media_content_id: 'emby-item-2', entity_picture: '/new.jpg',
  }), { previous: persistent });
  assert.equal(fresh.metadataStale, false);
  assert.equal(fresh.title, 'New series');
  assert.equal(fresh.artwork, '/new.jpg');
});

test('preserves stale-app provenance across idle, off and missing-entity gaps', () => {
  const attrs = {
    media_title: 'Old Plex film',
    media_content_id: 'plex-123',
    entity_picture: '/old-plex.jpg',
  };
  let previous = buildDevice(configured(), stateEntity('playing', { ...attrs, app_name: 'Plex' }));

  const idle = buildDevice(configured(), stateEntity('idle', attrs), { previous });
  assert.equal(idle.appName, null);
  assert.equal(idle.appIdentity, 'plex');
  previous = buildDevice(configured(), stateEntity('playing', { ...attrs, app_name: 'Emby' }), { previous: idle });
  assert.equal(previous.metadataStale, true);
  assert.equal(previous.artwork, null);

  const off = buildDevice(configured(), stateEntity('off', {}), { previous });
  assert.equal(off.appName, null);
  const missing = buildDevice(configured(), null, { previous: off });
  const resumed = buildDevice(configured(), stateEntity('playing', { ...attrs, app_name: 'Emby' }), { previous: missing });
  assert.equal(resumed.metadataStale, true);
  assert.equal(resumed.title, 'Media playing');
  assert.equal(resumed.artwork, null);

  const fresh = buildDevice(configured(), stateEntity('playing', {
    app_name: 'Emby', media_title: 'New film', media_content_id: 'emby-987', entity_picture: '/new.jpg',
  }), { previous: resumed });
  assert.equal(fresh.metadataStale, false);
  assert.equal(fresh.title, 'New film');
  assert.equal(fresh.artwork, '/new.jpg');
});

const plexMetadata = {
  app_name: 'Plex', media_title: 'Old Plex film', media_content_id: 'plex-123',
  entity_picture: '/old-plex.jpg', media_position: 15, media_duration: 90,
};

test('rejects inherited programme, artwork and progress after empty inactive gaps before switching apps', () => {
  for (const gapState of ['idle', 'off', 'unavailable', 'unknown', null]) {
    let previous = buildDevice(configured(), stateEntity('playing', plexMetadata));
    for (let count = 0; count < 2; count += 1) {
      previous = buildDevice(configured(), gapState === null ? null : stateEntity(gapState), { previous });
    }
    const switched = buildDevice(configured(), stateEntity('playing', {
      ...plexMetadata, app_name: 'Emby',
    }), { previous });
    assert.equal(switched.metadataStale, true, `gap: ${gapState}`);
    assert.equal(switched.title, 'Media playing');
    assert.equal(switched.detail, 'Programme information unavailable');
    assert.equal(switched.artwork, null);
    assert.equal(switched.progress, null);
  }
});

test('artwork and progress refreshes do not validate inherited programme fields', () => {
  let previous = buildDevice(configured(), stateEntity('playing', plexMetadata));
  previous = buildDevice(configured(), stateEntity('playing', {
    ...plexMetadata, app_name: 'Emby',
  }), { previous });
  for (const picture of ['/new-emby.jpg', '/newer-emby.jpg']) {
    previous = buildDevice(configured(), stateEntity('playing', {
      ...plexMetadata, app_name: 'Emby', entity_picture: picture,
      media_position: 25, media_duration: 120, media_position_updated_at: '2026-10-12T10:00:00Z',
    }), { previous });
    assert.equal(previous.metadataStale, true);
    assert.equal(previous.title, 'Media playing');
    assert.equal(previous.detail, 'Programme information unavailable');
    assert.equal(previous.progress, null);
    assert.equal(previous.artwork, picture, 'fresh artwork is independent of stale programme fields');
  }
  const fresh = buildDevice(configured(), stateEntity('playing', {
    ...plexMetadata, app_name: 'Emby', media_title: 'New Emby film', media_content_id: 'emby-456',
    entity_picture: '/newer-emby.jpg',
  }), { previous });
  assert.equal(fresh.metadataStale, false);
  assert.equal(fresh.title, 'New Emby film');
  assert.equal(fresh.artwork, '/newer-emby.jpg');
  assert.equal(fresh.progress.position, 15);
});

test('attributes first observed or refreshed while inactive retain their source app', () => {
  for (const state of ['idle', 'off', 'unavailable', 'unknown']) {
    for (const initial of [null, buildDevice(configured(), stateEntity('playing', {
      ...plexMetadata, media_title: 'Earlier Plex film', entity_picture: '/earlier.jpg',
    }))]) {
      const inactive = buildDevice(configured(), stateEntity(state, plexMetadata), { previous: initial });
      assert.equal(inactive.title, null);
      assert.equal(inactive.artwork, null);
      const switched = buildDevice(configured(), stateEntity('playing', {
        ...plexMetadata, app_name: 'Emby',
      }), { previous: inactive });
      assert.equal(switched.metadataStale, true, state);
      assert.equal(switched.title, 'Media playing');
      assert.equal(switched.artwork, null);
      assert.equal(switched.progress, null);
    }
  }
});

test('fresh programme fields do not validate inherited artwork from another app', () => {
  const previous = buildDevice(configured(), stateEntity('playing', plexMetadata));
  const fresh = buildDevice(configured(), stateEntity('playing', {
    ...plexMetadata, app_name: 'Emby', media_title: 'New film', media_content_id: 'emby-456',
  }), { previous });
  assert.equal(fresh.title, 'New film');
  assert.equal(fresh.metadataStale, false);
  assert.equal(fresh.artwork, null);
  const withPicture = buildDevice(configured(), stateEntity('playing', {
    ...plexMetadata, app_name: 'Emby', media_title: 'New film', media_content_id: 'emby-456',
    entity_picture: '/emby.jpg',
  }), { previous: fresh });
  assert.equal(withPicture.artwork, '/emby.jpg');
});

test('empty new-app updates and inactive inherited attributes do not take ownership of old metadata', () => {
  let previous = buildDevice(configured(), stateEntity('playing', plexMetadata));
  for (const entity of [
    stateEntity('off', { ...plexMetadata, app_name: 'Emby' }),
    stateEntity('playing', { app_name: 'Emby' }),
    stateEntity('unavailable'),
    null,
  ]) previous = buildDevice(configured(), entity, { previous });
  const inherited = buildDevice(configured(), stateEntity('playing', {
    ...plexMetadata, app_name: 'Emby',
  }), { previous });
  assert.equal(inherited.metadataStale, true);
  assert.equal(inherited.title, 'Media playing');
  assert.equal(inherited.artwork, null);
  assert.equal(inherited.progress, null);
});

test('metadata history is isolated by entity even when another room previous model is supplied', () => {
  const den = buildDevice(configured(), stateEntity('playing', plexMetadata));
  const study = buildDevice(configured('media_player.study'), stateEntity('playing', {
    ...plexMetadata, app_name: 'Emby',
  }), { previous: den });
  assert.equal(study.metadataStale, false);
  assert.equal(study.title, 'Old Plex film');
  assert.equal(study.artwork, '/old-plex.jpg');
  const denSwitch = buildDevice(configured(), stateEntity('playing', {
    ...plexMetadata, app_name: 'Emby',
  }), { previous: den });
  assert.equal(denSwitch.metadataStale, true);
  const studyUpdate = buildDevice(configured('media_player.study'), stateEntity('paused', {
    ...plexMetadata, app_name: 'Emby',
  }), { previous: study });
  assert.equal(studyUpdate.metadataStale, false);
  assert.equal(studyUpdate.title, 'Old Plex film');
});

test('same-app resume and returning to the original app retain legitimate metadata', () => {
  const first = buildDevice(configured(), stateEntity('playing', plexMetadata));
  const gap = buildDevice(configured(), stateEntity('off'), { previous: first });
  const resumed = buildDevice(configured(), stateEntity('paused', plexMetadata), { previous: gap });
  assert.equal(resumed.metadataStale, false);
  assert.equal(resumed.title, 'Old Plex film');
  assert.equal(resumed.artwork, '/old-plex.jpg');
  assert.equal(resumed.progress.position, 15);
  const switched = buildDevice(configured(), stateEntity('playing', {
    ...plexMetadata, app_name: 'Emby',
  }), { previous: first });
  const returned = buildDevice(configured(), stateEntity('playing', plexMetadata), { previous: switched });
  assert.equal(returned.metadataStale, false);
  assert.equal(returned.title, 'Old Plex film');
});

test('keeps a selected active device and falls back by status across any device count', () => {
  const devices = [
    { entity: 'media_player.one', status: 'idle', active: false },
    { entity: 'media_player.two', status: 'paused', active: true },
    { entity: 'media_player.three', status: 'playing', active: true },
    { entity: 'media_player.four', status: 'app', active: true },
  ];
  assert.equal(chooseFeatured(devices, 'media_player.two'), devices[1]);
  assert.equal(chooseFeatured(devices, 'media_player.one'), devices[2]);
  assert.equal(chooseFeatured(devices.slice(0, 2), 'missing'), devices[1]);
  assert.equal(chooseFeatured([{ status: 'idle', active: false }], null), null);
  assert.equal(chooseFeatured([], null), null);
});

test('distinguishes an app-name fallback from a real programme title with the same name', () => {
  const app = { app_id: 'ar.tvplayer.tv' };
  assert.equal(buildDevice(configured(), stateEntity('playing', app)).titleIsAppFallback, true);
  assert.equal(buildDevice(configured(), stateEntity('on', app)).titleIsAppFallback, true);
  const programme = buildDevice(configured(), stateEntity('playing', { ...app, media_title: 'TiviMate' }));
  assert.equal(programme.title, 'TiviMate');
  assert.equal(programme.titleIsAppFallback, false);
  assert.equal(buildDevice(configured(), stateEntity('playing')).titleIsAppFallback, false);
});

test('formats durations consistently', () => {
  assert.equal(formatTime(0), '0:00');
  assert.equal(formatTime(65), '1:05');
  assert.equal(formatTime(3605), '1:00:05');
  assert.equal(formatTime(-1), '–:––');
  assert.equal(formatTime(Number.NaN), '–:––');
});
