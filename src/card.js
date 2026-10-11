import { normalizeConfig, buildDevice, chooseFeatured, formatTime } from './media-model.js';
import { styles } from './styles.js';

// Brand assets are optional, local files. A missing image always leaves its name.
const LOGOS = {
  plex: new URL('../assets/plex.png', import.meta.url).href,
  emby: new URL('../assets/emby.png', import.meta.url).href,
  tivimate: new URL('../assets/tivimate.png', import.meta.url).href,
  silo: new URL('../assets/silo.png', import.meta.url).href,
};
const ICONS = {
  tv: '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
  pause: '<path d="M8 5v14M16 5v14"/>',
  play: '<path d="m8 5 11 7-11 7Z"/>',
  chevron: '<path d="m9 5 7 7-7 7"/>',
};
function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}
function icon(name, className = '') {
  const span = node('span', className);
  span.setAttribute('aria-hidden', 'true');
  // This template contains only fixed, locally authored icon paths.
  span.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg>`;
  return span;
}

export class NmdMediaCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    const style = node('style');
    style.textContent = styles;
    this._card = node('ha-card');
    this._card.setAttribute('aria-label', 'Media');
    this._announcement = node('span', 'sr-only');
    this._announcement.setAttribute('aria-live', 'polite');
    this.shadowRoot.append(style, this._card, this._announcement);
    this._previous = new Map();
    this._pending = new Set();
    this._selected = null;
    this._renderKey = '';
    this._error = '';
  }

  setConfig(config) {
    this._config = normalizeConfig(config);
    this._previous.clear();
    this._selected = null;
    this._error = '';
    this._renderKey = '';
    this._update();
  }

  set hass(hass) {
    this._hass = hass;
    this._update();
  }
  get hass() { return this._hass; }

  connectedCallback() {
    // Tick only the progress display; state and controls always come from HA.
    if (!this._timer) this._timer = setInterval(() => this._updateProgress(), 1000);
    this._update();
  }
  disconnectedCallback() {
    clearInterval(this._timer);
    this._timer = null;
  }
  getCardSize() { return Math.max(2, Math.ceil(this._card.getBoundingClientRect().height / 50)); }
  getGridOptions() { return { columns: 12, min_columns: 6 }; }

  _devices() {
    const states = this._hass?.states ?? {};
    return this._config.devices.map(device => {
      const value = buildDevice(device, states[device.entity], {
        previous: this._previous.get(device.entity),
        platform: this._hass?.entities?.[device.entity]?.platform,
      });
      this._previous.set(device.entity, value);
      return value;
    });
  }

  _update() {
    if (!this._config) return;
    this._views = this._devices();
    const featured = chooseFeatured(this._views, this._selected);
    this._selected = featured?.entity ?? null;
    // Position changes do not replace buttons or images and disturb keyboard focus.
    const renderKey = JSON.stringify({
      views: this._views.map(({progress, ...view}) => ({...view, hasProgress:!!progress})),
      selected: this._selected, pending:[...this._pending], error:this._error,
    });
    if (renderKey !== this._renderKey) {
      this._renderKey = renderKey;
      this._render(featured);
    }
    this._updateProgress();
  }

  _render(featured) {
    const focusKey = this.shadowRoot.activeElement?.dataset.focus;
    this._card.replaceChildren();
    this._progress = null;
    if (!featured) {
      this._renderIdle();
    } else {
      this._renderFeature(featured);
      const others = this._views.filter(view => view.entity !== featured.entity);
      if (others.length) {
        const footer = node('div', 'others');
        for (const view of others.filter(view => view.active)) footer.append(this._preview(view));
        const inactive = others.filter(view => !view.active);
        if (inactive.length) {
          const rest = node('div', 'rest');
          for (const view of inactive) rest.append(node('span', '', `${view.name} · ${view.statusLabel}`));
          footer.append(rest);
        }
        this._card.append(footer);
      }
    }
    if (this._error) {
      const error = node('p','error',this._error);
      error.setAttribute('role','alert');
      this._card.append(error);
    }
    if (focusKey) {
      const controls = [...this.shadowRoot.querySelectorAll('[data-focus]')];
      // After a room switch the previous preview disappears; keep focus on a preview.
      const next = controls.find(control => control.dataset.focus === focusKey)
        ?? (focusKey.startsWith('room:') ? controls.find(control => control.dataset.focus.startsWith('room:')) : null)
        ?? controls[0];
      next?.focus({preventScroll:true});
    }
  }

  _renderIdle() {
    const idle = node('div','idle');
    const top = node('div','idle-top');
    const titleGroup = node('div');
    const uncertain = this._views.some(view => ['unknown','unavailable'].includes(view.status));
    const allUnavailable = this._views.every(view => view.status === 'unavailable');
    titleGroup.append(node('div','brand','MEDIA'),node('h2','',allUnavailable ? 'Devices unavailable' : uncertain ? 'No confirmed playback' : 'Nothing playing'));
    top.append(icon('tv','tv'), titleGroup);
    const statuses = node('div','statuses');
    for (const view of this._views) {
      const status = node('span');
      status.append(node('span','status-name',view.name),node('span','',view.statusLabel));
      statuses.append(status);
    }
    idle.append(top,statuses);
    this._card.append(idle);
  }

  _image(url, className) {
    const image = node('img',className);
    image.alt = '';
    image.hidden = true;
    image.referrerPolicy = 'no-referrer';
    image.addEventListener('load', () => { image.hidden = false; });
    image.addEventListener('error', () => { image.hidden = true; });
    image.src = this._resolveImage(url);
    return image;
  }

  _resolveImage(url) {
    return url.startsWith('/') && this._hass?.hassUrl ? this._hass.hassUrl(url) : url;
  }

  _app(view) {
    const app = node('span',view.appKey === 'tivimate' ? 'app app-tivimate' : 'app');
    if (!view.appName) return app;
    app.setAttribute('role','img');
    app.setAttribute('aria-label',view.appName);
    const text = node('span','',view.appName);
    text.setAttribute('aria-hidden','true');
    const url = Object.hasOwn(this._config.app_logos,view.appKey) ? this._config.app_logos[view.appKey]
      : Object.hasOwn(LOGOS,view.appKey) ? LOGOS[view.appKey] : null;
    if (url) {
      const image = this._image(url,'');
      image.width = 24;
      image.height = 24;
      image.addEventListener('load', () => { text.hidden = true; });
      image.addEventListener('error', () => { text.hidden = false; });
      app.append(image);
    }
    app.append(text);
    return app;
  }

  _renderFeature(view) {
    const feature = node('section','feature');
    feature.setAttribute('aria-label',`${view.name}: ${view.statusLabel}`);
    if (view.artwork) feature.append(this._image(view.artwork,'backdrop'));
    const top = node('div','topline');
    top.append(node('span','room',view.name),node('span','state',`· ${view.statusLabel}`),this._app(view));
    const content = node('div','content');
    const text = node('div','title-group');
    if (!view.titleIsAppFallback) text.append(node('h2','title',view.title));
    if (view.detail) text.append(node('div','detail',view.detail));
    content.append(text);
    if (view.action) {
      const button = node('button','control');
      button.type = 'button';
      button.dataset.focus = `control:${view.entity}`;
      const pause = view.action === 'media_pause';
      button.setAttribute('aria-label',`${pause ? 'Pause' : 'Resume'} ${view.name}`);
      const pending = this._pending.has(view.entity);
      // Remain focusable while awaiting HA; the click handler rejects duplicates.
      button.setAttribute('aria-disabled',String(pending));
      button.setAttribute('aria-busy',String(pending));
      button.append(icon(pause ? 'pause' : 'play'));
      button.addEventListener('click', () => this._control(view.entity));
      content.append(button);
    }
    feature.append(top,content);
    if (view.progress) {
      const timing = node('div','timing');
      const elapsed = node('span');
      const duration = node('span');
      const track = node('div','track');
      track.setAttribute('role','progressbar');
      track.setAttribute('aria-label',`${view.name} playback progress`);
      track.setAttribute('aria-valuemin','0');
      track.setAttribute('aria-valuemax','100');
      const fill = node('div','fill');
      track.append(fill);
      timing.append(elapsed,track,duration);
      feature.append(timing);
      this._progress = {entity:view.entity,elapsed,duration,track,fill};
    } else {
      const limited = ['app','on'].includes(view.status) ? 'Playback not confirmed' : 'Progress unavailable';
      feature.append(node('div','limited',limited));
    }
    this._card.append(feature);
  }

  _preview(view) {
    const button = node('button','other');
    button.type = 'button';
    button.dataset.focus = `room:${view.entity}`;
    button.setAttribute('aria-label',`Show ${view.name}: ${view.title}`);
    if (view.artwork) button.append(this._image(view.artwork,'thumb'));
    const text = node('span','other-text');
    text.append(node('div','other-meta',`${view.name} · ${view.statusLabel}${view.appName ? ` · ${view.appName}` : ''}`),node('div','other-title',view.titleIsAppFallback ? view.detail : view.title));
    button.append(text,icon('chevron','chevron'));
    button.addEventListener('click', () => {
      this._selected = view.entity;
      this._error = '';
      this._update();
      this._announcement.textContent = `Featured room: ${view.name}.`;
    });
    return button;
  }

  _updateProgress() {
    if (!this._progress || !this._config) return;
    const {entity,elapsed,duration,track,fill} = this._progress;
    const device = this._config.devices.find(item => item.entity === entity);
    if (!device) return;
    const view = buildDevice(device,this._hass?.states?.[entity], {
      previous:this._previous.get(entity), platform:this._hass?.entities?.[entity]?.platform,
    });
    if (!view.progress) return;
    elapsed.textContent = formatTime(view.progress.position);
    duration.textContent = formatTime(view.progress.duration);
    fill.style.width = `${view.progress.percent}%`;
    track.setAttribute('aria-valuenow',String(Math.round(view.progress.percent)));
    track.setAttribute('aria-valuetext',`${elapsed.textContent} of ${duration.textContent}`);
  }

  async _control(entity) {
    if (this._pending.has(entity)) return;
    // Re-read capabilities and state when clicked, never use a stale rendered action.
    const device = this._config.devices.find(item => item.entity === entity);
    if (!device) return;
    const view = buildDevice(device,this._hass?.states?.[entity], {
      previous:this._previous.get(entity), platform:this._hass?.entities?.[entity]?.platform,
    });
    if (!view.action || !this._hass?.callService) return;
    this._pending.add(entity);
    const requestConfig = this._config;
    this._error = '';
    this._update();
    try {
      await this._hass.callService('media_player',view.action,{entity_id:entity});
    } catch {
      // Do not expose backend errors or token-bearing URLs in the dashboard.
      if (this._config === requestConfig) this._error = `Could not ${view.action === 'media_pause' ? 'pause' : 'resume'} ${view.name}. Try again.`;
    } finally {
      this._pending.delete(entity);
      this._update();
    }
  }
}

if (!customElements.get('nmd-media-card')) customElements.define('nmd-media-card',NmdMediaCard);
window.customCards = window.customCards || [];
if (!window.customCards.some(card => card.type === 'nmd-media-card')) {
  window.customCards.push({type:'nmd-media-card',name:'NMD Media Card',description:'Compact playback across your rooms.',preview:false});
}
