/**
 * Future adapter registration layer.
 * Not yet integrated into the standalone engine flow.
 */


export class FrameworkRegistry {

  constructor() {
    this.registry = {};
  }

  register(key, adapter) {
    this.registry[key] = adapter;
  }

  get(key) {
    return this.registry[key];
  }

  list() {
    return Object.keys(this.registry);
  }

}