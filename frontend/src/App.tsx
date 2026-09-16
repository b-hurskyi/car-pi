import "./App.css";

export function App() {
  return (
    <main className="app-shell">
      <section className="status-panel" aria-labelledby="app-title">
        <p className="eyebrow">Development build</p>
        <h1 id="app-title">Car Computer</h1>
        <p className="status-text">System online</p>
      </section>
    </main>
  );
}
