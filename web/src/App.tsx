import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  apiBase,
  graphExecute,
  healthLive,
  healthReady,
  listUsers,
  login,
  me,
  parseApiError,
  register
} from "./api";
import { detectLocale, type Locale, t } from "./i18n";
import type { ChatMessage, UserResponse } from "./types";

type ViewId = "assistant" | "identity" | "admin" | "system";

type StatusMessage = {
  key: string;
  params?: Record<string, string | number>;
};

const STORAGE_KEY = "tripy_web_access_token";

const VIEWS: Array<{ id: ViewId; labelKey: string; descKey: string }> = [
  { id: "assistant", labelKey: "view.assistant", descKey: "view.assistantDesc" },
  { id: "identity", labelKey: "view.identity", descKey: "view.identityDesc" },
  { id: "admin", labelKey: "view.admin", descKey: "view.adminDesc" },
  { id: "system", labelKey: "view.system", descKey: "view.systemDesc" }
];

const viewPanelId = (id: ViewId) => `view-panel-${id}`;
const viewTabId = (id: ViewId) => `view-tab-${id}`;

const formatTimestamp = (value: string, locale: Locale) => {
  const dt = new Date(value);
  if (Number.isNaN(dt.getTime())) {
    return value;
  }
  return dt.toLocaleString(locale === "zh" ? "zh-CN" : "en-US");
};

const buildMessage = (
  role: ChatMessage["role"],
  text: string,
  interrupted = false
): ChatMessage => ({
  id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
  role,
  text,
  interrupted,
  createdAt: new Date().toISOString()
});

export default function App() {
  const initialLocale = detectLocale();

  const [locale, setLocale] = useState<Locale>(initialLocale);
  const [activeView, setActiveView] = useState<ViewId>("assistant");

  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("ChangeMe123!");

  const [registerUsername, setRegisterUsername] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [registerPassengerId, setRegisterPassengerId] = useState("");

  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));
  const [profile, setProfile] = useState<UserResponse | null>(null);
  const [roles, setRoles] = useState<string[]>([]);
  const [permissions, setPermissions] = useState<string[]>([]);

  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusMessage>({ key: "status.ready" });

  const [query, setQuery] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const [users, setUsers] = useState<UserResponse[]>([]);
  const [healthState, setHealthState] = useState({
    live: "unknown",
    ready: "unknown",
    checkedAt: "-"
  });

  const tt = (key: string, params?: Record<string, string | number>) => t(locale, key, params);

  const isAuthed = Boolean(token);
  const canAdminUsers = permissions.includes("users:read");
  const canGraphExecute = permissions.includes("graph:execute");

  const messageCount = useMemo(() => messages.length, [messages.length]);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const runAction = async (action: string, fn: () => Promise<void>) => {
    setBusyAction(action);
    try {
      await fn();
    } finally {
      setBusyAction(null);
    }
  };

  const loadProfile = async (accessToken: string) => {
    const current = await me(accessToken);
    setProfile(current);
    setRoles(current.roles);
    setPermissions(current.permissions);
  };

  useEffect(() => {
    const run = async () => {
      if (!token) {
        setProfile(null);
        setRoles([]);
        setPermissions([]);
        return;
      }
      try {
        await loadProfile(token);
      } catch (error) {
        const reason = parseApiError(error);
        setToken(null);
        localStorage.removeItem(STORAGE_KEY);
        setStatus({ key: "status.sessionExpired", params: { reason } });
      }
    };
    void run();
  }, [token]);

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    await runAction("login", async () => {
      try {
        setStatus({ key: "status.signingIn" });
        const result = await login(username, password);
        localStorage.setItem(STORAGE_KEY, result.access_token);
        setToken(result.access_token);
        setRoles(result.roles);
        setPermissions(result.permissions);
        const roleText = result.roles.join(", ") || tt("identity.none");
        setStatus({ key: "status.signedIn", params: { roles: roleText } });
      } catch (error) {
        setStatus({ key: "status.loginFailed", params: { reason: parseApiError(error) } });
      }
    });
  };

  const handleRegister = async (event: FormEvent) => {
    event.preventDefault();
    if (!registerUsername || !registerPassword) {
      return;
    }
    await runAction("register", async () => {
      try {
        await register({
          username: registerUsername,
          password: registerPassword,
          passenger_id: registerPassengerId || undefined
        });
        setRegisterUsername("");
        setRegisterPassword("");
        setRegisterPassengerId("");
        setStatus({ key: "status.userRegistered" });
      } catch (error) {
        setStatus({ key: "status.registerFailed", params: { reason: parseApiError(error) } });
      }
    });
  };

  const handleSignOut = () => {
    setToken(null);
    setProfile(null);
    setRoles([]);
    setPermissions([]);
    setMessages([]);
    setThreadId(null);
    setUsers([]);
    localStorage.removeItem(STORAGE_KEY);
    setStatus({ key: "status.signedOut" });
  };

  const handleCheckHealth = async () => {
    await runAction("health", async () => {
      try {
        const [live, ready] = await Promise.all([healthLive(), healthReady()]);
        const checkedAt = new Date().toLocaleString(locale === "zh" ? "zh-CN" : "en-US");
        setHealthState({ live: live.status, ready: ready.status, checkedAt });
        setStatus({ key: "status.healthPassed", params: { time: checkedAt } });
      } catch (error) {
        setStatus({ key: "status.healthFailed", params: { reason: parseApiError(error) } });
      }
    });
  };

  const handleSend = async () => {
    if (!query || !token || !canGraphExecute) {
      return;
    }
    const prompt = query.trim();
    if (!prompt) {
      return;
    }

    await runAction("graph", async () => {
      const userMessage = buildMessage("user", prompt);
      setMessages((prev) => [...prev, userMessage]);
      setQuery("");

      try {
        const result = await graphExecute(token, prompt, threadId);
        setThreadId(result.thread_id);
        setMessages((prev) => [
          ...prev,
          buildMessage("assistant", result.assistant, result.interrupted)
        ]);
        if (result.interrupted) {
          setStatus({ key: "status.graphInterrupted" });
        } else {
          setStatus({ key: "status.graphReady" });
        }
      } catch (error) {
        const reason = parseApiError(error);
        setMessages((prev) => [...prev, buildMessage("system", `Request failed: ${reason}`)]);
        setStatus({ key: "status.graphFailed", params: { reason } });
      }
    });
  };

  const handleLoadUsers = async () => {
    if (!token || !canAdminUsers) {
      return;
    }
    await runAction("users", async () => {
      try {
        const records = await listUsers(token, 0, 200);
        setUsers(records);
        setStatus({ key: "status.usersLoaded", params: { count: records.length } });
      } catch (error) {
        setStatus({ key: "status.usersFailed", params: { reason: parseApiError(error) } });
      }
    });
  };

  return (
    <div className="tripy-shell">
      <a href="#main-content" className="skip-link">
        {tt("skip.main")}
      </a>

      <header className="tripy-hero" role="banner">
        <div className="hero-panel">
          <div className="hero-topbar">
            <p className="overline">{tt("hero.overline")}</p>
            <div className="lang-switch" role="group" aria-label={tt("lang.switch")}> 
              <button
                type="button"
                className={`lang-btn ${locale === "en" ? "active" : ""}`}
                aria-pressed={locale === "en"}
                onClick={() => setLocale("en")}
                data-testid="lang-en"
              >
                {tt("lang.en")}
              </button>
              <button
                type="button"
                className={`lang-btn ${locale === "zh" ? "active" : ""}`}
                aria-pressed={locale === "zh"}
                onClick={() => setLocale("zh")}
                data-testid="lang-zh"
              >
                {tt("lang.zh")}
              </button>
            </div>
          </div>
          <h1>{tt("hero.title")}</h1>
          <p className="hero-copy">{tt("hero.copy")}</p>
          <div className="chip-row" aria-label="stack">
            <span>FastAPI</span>
            <span>LangGraph</span>
            <span>RBAC</span>
            <span>OpenTelemetry</span>
          </div>
        </div>

        <div className="hero-panel telemetry-panel" aria-label="system metrics">
          <p className="mini-label">{tt("env.title")}</p>
          <h3>{tt("env.snapshot")}</h3>
          <p className="meta-line">
            {tt("env.apiBase")}: <code>{apiBase}</code>
          </p>
          <div className="health-grid">
            <article>
              <small>{tt("env.live")}</small>
              <strong>{healthState.live}</strong>
            </article>
            <article>
              <small>{tt("env.ready")}</small>
              <strong>{healthState.ready}</strong>
            </article>
          </div>
          <p className="meta-line">
            {tt("env.checked")}: {healthState.checkedAt}
          </p>
          <button
            type="button"
            className="ghost-btn"
            onClick={handleCheckHealth}
            disabled={busyAction === "health"}
          >
            {busyAction === "health" ? tt("env.checking") : tt("env.runHealth")}
          </button>
        </div>
      </header>

      <div className="layout">
        <aside className="rail">
          <section className="card" aria-label="session forms">
            <div className="card-head">
              <h2>{tt("session.title")}</h2>
              <span className={`state-chip ${isAuthed ? "online" : "offline"}`}>
                {isAuthed ? tt("session.authed") : tt("session.guest")}
              </span>
            </div>

            <form className="stack" onSubmit={handleLogin}>
              <label htmlFor="username">{tt("session.username")}</label>
              <input
                id="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
              />

              <label htmlFor="password">{tt("session.password")}</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
              />

              <div className="button-row">
                <button
                  type="submit"
                  disabled={busyAction === "login" || isAuthed}
                  data-testid="login-button"
                >
                  {busyAction === "login" ? tt("status.signingIn") : tt("session.signIn")}
                </button>
                <button
                  type="button"
                  className="ghost-btn"
                  onClick={handleSignOut}
                  disabled={!isAuthed}
                >
                  {tt("session.signOut")}
                </button>
              </div>
            </form>

            <form className="stack register" onSubmit={handleRegister}>
              <h4>{tt("register.title")}</h4>
              <label htmlFor="register-user">{tt("register.username")}</label>
              <input
                id="register-user"
                value={registerUsername}
                onChange={(event) => setRegisterUsername(event.target.value)}
              />

              <label htmlFor="register-pass">{tt("register.password")}</label>
              <input
                id="register-pass"
                type="password"
                value={registerPassword}
                onChange={(event) => setRegisterPassword(event.target.value)}
              />

              <label htmlFor="register-passenger">{tt("register.passenger")}</label>
              <input
                id="register-passenger"
                value={registerPassengerId}
                onChange={(event) => setRegisterPassengerId(event.target.value)}
              />

              <button type="submit" className="ghost-btn" disabled={busyAction === "register"}>
                {busyAction === "register" ? tt("register.creating") : tt("register.submit")}
              </button>
            </form>
          </section>

          <section className="card nav-card" aria-label="workspace navigation">
            <h2>{tt("workspace.title")}</h2>
            <div className="view-list" role="tablist" aria-label={tt("workspace.title")}>
              {VIEWS.map((view) => (
                <button
                  id={viewTabId(view.id)}
                  key={view.id}
                  type="button"
                  role="tab"
                  aria-selected={activeView === view.id}
                  aria-controls={viewPanelId(view.id)}
                  className={`view-btn ${activeView === view.id ? "active" : ""}`}
                  onClick={() => setActiveView(view.id)}
                  data-testid={view.id === "admin" ? "tab-admin" : undefined}
                >
                  <span>{tt(view.labelKey)}</span>
                  <small>{tt(view.descKey)}</small>
                </button>
              ))}
            </div>
          </section>
        </aside>

        <main id="main-content" className="main-panel" tabIndex={-1}>
          {activeView === "assistant" && (
            <section
              className="card card-fill"
              id={viewPanelId("assistant")}
              role="tabpanel"
              aria-labelledby={viewTabId("assistant")}
            >
              <div className="card-head">
                <h2>{tt("assistant.title")}</h2>
                <span className="text-muted">
                  {tt("assistant.thread")}: {threadId || tt("assistant.newThread")}
                </span>
              </div>

              <p className="text-muted">{tt("assistant.tip")}</p>

              {!canGraphExecute && isAuthed && (
                <p className="text-warn">
                  {tt("assistant.noPermission")} <code>graph:execute</code>
                </p>
              )}

              <div className="composer">
                <textarea
                  rows={4}
                  placeholder={tt("assistant.placeholder")}
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  data-testid="assistant-input"
                  onKeyDown={(event) => {
                    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
                      event.preventDefault();
                      void handleSend();
                    }
                  }}
                />
                <div className="button-row">
                  <button
                    type="button"
                    onClick={() => void handleSend()}
                    disabled={!isAuthed || !query.trim() || busyAction === "graph" || !canGraphExecute}
                    data-testid="assistant-send"
                  >
                    {busyAction === "graph" ? tt("assistant.sending") : tt("assistant.send")}
                  </button>
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={() => {
                      setMessages([]);
                      setThreadId(null);
                    }}
                    disabled={messageCount === 0}
                  >
                    {tt("assistant.clear")}
                  </button>
                </div>
              </div>

              <div className="timeline" aria-live="polite">
                {messages.length === 0 ? (
                  <div className="empty-state">
                    <h4>{tt("assistant.emptyTitle")}</h4>
                    <p>{tt("assistant.emptyDesc")}</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <article key={message.id} className={`msg msg-${message.role}`}>
                      <header>
                        <strong>{message.role}</strong>
                        <small>{formatTimestamp(message.createdAt, locale)}</small>
                      </header>
                      <p>{message.text}</p>
                      {message.interrupted && (
                        <span className="interrupt-chip">{tt("assistant.interrupted")}</span>
                      )}
                    </article>
                  ))
                )}
              </div>
            </section>
          )}

          {activeView === "identity" && (
            <section
              className="card card-fill"
              id={viewPanelId("identity")}
              role="tabpanel"
              aria-labelledby={viewTabId("identity")}
            >
              <div className="card-head">
                <h2>{tt("identity.title")}</h2>
                <span className="text-muted">{profile?.username || tt("identity.notSigned")}</span>
              </div>

              {profile ? (
                <div className="identity-grid">
                  <article>
                    <h4>{tt("identity.profile")}</h4>
                    <p>
                      <strong>{tt("identity.userId")}:</strong> {profile.id}
                    </p>
                    <p>
                      <strong>{tt("identity.passengerId")}:</strong> {profile.passenger_id || "-"}
                    </p>
                    <p>
                      <strong>{tt("identity.email")}:</strong> {profile.email || "-"}
                    </p>
                    <p>
                      <strong>{tt("identity.userStatus")}:</strong>{" "}
                      {profile.is_active ? tt("identity.active") : tt("identity.disabled")}
                    </p>
                  </article>

                  <article>
                    <h4>{tt("identity.roles")}</h4>
                    <div className="pill-wrap">
                      {roles.length
                        ? roles.map((entry) => <span key={entry}>{entry}</span>)
                        : [<span key="none">{tt("identity.none")}</span>]}
                    </div>
                  </article>

                  <article>
                    <h4>{tt("identity.permissions")}</h4>
                    <div className="pill-wrap">
                      {permissions.length
                        ? permissions.map((entry) => <span key={entry}>{entry}</span>)
                        : [<span key="none">{tt("identity.none")}</span>]}
                    </div>
                  </article>
                </div>
              ) : (
                <p className="text-muted">{tt("identity.prompt")}</p>
              )}
            </section>
          )}

          {activeView === "admin" && (
            <section
              className="card card-fill"
              id={viewPanelId("admin")}
              role="tabpanel"
              aria-labelledby={viewTabId("admin")}
              data-testid="admin-panel"
            >
              <div className="card-head">
                <h2>{tt("admin.title")}</h2>
                <button
                  type="button"
                  className="ghost-btn"
                  onClick={handleLoadUsers}
                  disabled={!isAuthed || !canAdminUsers || busyAction === "users"}
                  data-testid="admin-refresh-users"
                >
                  {busyAction === "users" ? tt("admin.loading") : tt("admin.refresh")}
                </button>
              </div>

              {!canAdminUsers && isAuthed && (
                <p className="text-warn">
                  {tt("admin.noPermission")} <code>users:read</code>
                </p>
              )}

              {!isAuthed && <p className="text-muted">{tt("admin.signInPrompt")}</p>}

              <div className="table-shell">
                <table>
                  <caption className="sr-only">Admin users</caption>
                  <thead>
                    <tr>
                      <th>{tt("admin.id")}</th>
                      <th>{tt("admin.username")}</th>
                      <th>{tt("admin.roles")}</th>
                      <th>{tt("admin.permissions")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="empty-cell">
                          {tt("admin.empty")}
                        </td>
                      </tr>
                    ) : (
                      users.map((entry) => (
                        <tr key={entry.id}>
                          <td>{entry.id}</td>
                          <td>{entry.username}</td>
                          <td>{entry.roles.join(", ") || "-"}</td>
                          <td>{entry.permissions.join(", ") || "-"}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {activeView === "system" && (
            <section
              className="card card-fill"
              id={viewPanelId("system")}
              role="tabpanel"
              aria-labelledby={viewTabId("system")}
            >
              <div className="card-head">
                <h2>{tt("system.title")}</h2>
              </div>

              <div className="identity-grid">
                <article>
                  <h4>{tt("system.connection")}</h4>
                  <p>
                    <strong>{tt("system.api")}:</strong> <code>{apiBase}</code>
                  </p>
                  <p>
                    <strong>{tt("env.live")}:</strong> {healthState.live}
                  </p>
                  <p>
                    <strong>{tt("env.ready")}:</strong> {healthState.ready}
                  </p>
                </article>

                <article>
                  <h4>{tt("system.session")}</h4>
                  <p>
                    <strong>{tt("system.authenticated")}:</strong>{" "}
                    {isAuthed ? tt("system.yes") : tt("system.no")}
                  </p>
                  <p>
                    <strong>{tt("system.roles")}:</strong> {roles.join(", ") || "-"}
                  </p>
                  <p>
                    <strong>{tt("system.permissions")}:</strong> {permissions.length}
                  </p>
                </article>

                <article>
                  <h4>{tt("system.activity")}</h4>
                  <p>
                    <strong>{tt("system.messages")}:</strong> {messageCount}
                  </p>
                  <p>
                    <strong>{tt("system.thread")}:</strong> {threadId || "-"}
                  </p>
                </article>
              </div>
            </section>
          )}
        </main>
      </div>

      <footer className="status-bar" aria-live="polite" data-testid="status-bar">
        {tt(status.key, status.params)}
      </footer>
    </div>
  );
}
