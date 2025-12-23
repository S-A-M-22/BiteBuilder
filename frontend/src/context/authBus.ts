const bus = new EventTarget();

export function emitLogout() {
  bus.dispatchEvent(new Event("logout"));
}

export function onLogout(cb: () => void) {
  const handler = () => cb();
  bus.addEventListener("logout", handler);
  return () => bus.removeEventListener("logout", handler);
}
