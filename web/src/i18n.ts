export type Locale = "en" | "zh";

type Primitive = string | number;
type MessageValue = string | ((params: Record<string, Primitive>) => string);
type Dictionary = Record<string, MessageValue>;

const messages: Record<Locale, Dictionary> = {
  en: {
    "lang.en": "EN",
    "lang.zh": "中文",
    "lang.switch": "Switch language",
    "skip.main": "Skip to main content",

    "status.ready": "Ready. Sign in and start a graph conversation.",
    "status.custom": ({ text }) => String(text),
    "status.signingIn": "Signing in...",
    "status.loginFailed": ({ reason }) => `Login failed: ${reason}`,
    "status.signedIn": ({ roles }) => `Signed in. ${roles}.`,
    "status.userRegistered": "User registered. You can login now.",
    "status.registerFailed": ({ reason }) => `Register failed: ${reason}`,
    "status.signedOut": "Signed out.",
    "status.healthPassed": ({ time }) => `Health checks passed at ${time}.`,
    "status.healthFailed": ({ reason }) => `Health check failed: ${reason}`,
    "status.graphInterrupted": "Graph requested interruption confirmation.",
    "status.graphReady": "Assistant response ready.",
    "status.graphFailed": ({ reason }) => `Graph execution failed: ${reason}`,
    "status.usersLoaded": ({ count }) => `Loaded ${count} users.`,
    "status.usersFailed": ({ reason }) => `Load users failed: ${reason}`,
    "status.sessionExpired": ({ reason }) => `Session expired: ${reason}`,

    "hero.overline": "Tripy Enterprise Console",
    "hero.title": "Graph-native travel assistant with production-grade governance.",
    "hero.copy": "Secure auth, RBAC, observability-ready backend, and a real-time operator surface for mission-critical workflows.",

    "env.title": "Environment",
    "env.snapshot": "System Snapshot",
    "env.apiBase": "API base",
    "env.live": "Live",
    "env.ready": "Ready",
    "env.checked": "Checked",
    "env.runHealth": "Run health checks",
    "env.checking": "Checking...",

    "session.title": "Session",
    "session.authed": "Authenticated",
    "session.guest": "Guest",
    "session.username": "Username",
    "session.password": "Password",
    "session.signIn": "Sign in",
    "session.signOut": "Sign out",

    "register.title": "Create user",
    "register.username": "Username",
    "register.password": "Password",
    "register.passenger": "Passenger ID (optional)",
    "register.submit": "Register",
    "register.creating": "Creating...",

    "workspace.title": "Workspace",
    "view.assistant": "Graph Assistant",
    "view.assistantDesc": "Threaded travel workflow",
    "view.identity": "Identity",
    "view.identityDesc": "Roles and permissions",
    "view.admin": "Admin",
    "view.adminDesc": "User inventory",
    "view.system": "System",
    "view.systemDesc": "Health and config",

    "assistant.title": "Graph Assistant",
    "assistant.thread": "Thread",
    "assistant.newThread": "new",
    "assistant.tip": "Press Cmd/Ctrl + Enter in the input box to send quickly.",
    "assistant.noPermission": "This user does not have graph:execute permission.",
    "assistant.placeholder": "Ask Tripy to plan or reason through a travel task...",
    "assistant.send": "Send",
    "assistant.sending": "Running graph...",
    "assistant.clear": "Clear thread",
    "assistant.emptyTitle": "No conversation yet",
    "assistant.emptyDesc": "Start with a request such as booking changes, policy checks, or route advice.",
    "assistant.interrupted": "Interrupted flow",

    "identity.title": "Identity & RBAC",
    "identity.notSigned": "Not signed in",
    "identity.prompt": "Sign in to inspect RBAC claims.",
    "identity.profile": "Profile",
    "identity.userId": "User ID",
    "identity.passengerId": "Passenger ID",
    "identity.email": "Email",
    "identity.userStatus": "Status",
    "identity.active": "active",
    "identity.disabled": "disabled",
    "identity.roles": "Roles",
    "identity.permissions": "Permissions",
    "identity.none": "none",

    "admin.title": "Admin Users",
    "admin.refresh": "Refresh users",
    "admin.loading": "Loading...",
    "admin.noPermission": "Missing users:read permission for admin list endpoint.",
    "admin.signInPrompt": "Sign in to use admin APIs.",
    "admin.id": "ID",
    "admin.username": "Username",
    "admin.roles": "Roles",
    "admin.permissions": "Permissions",
    "admin.empty": "No users loaded.",

    "system.title": "System Console",
    "system.connection": "Connection",
    "system.session": "Session",
    "system.activity": "Activity",
    "system.api": "API",
    "system.authenticated": "Authenticated",
    "system.yes": "yes",
    "system.no": "no",
    "system.roles": "Roles",
    "system.permissions": "Permissions",
    "system.messages": "Messages",
    "system.thread": "Thread"
  },
  zh: {
    "lang.en": "EN",
    "lang.zh": "中文",
    "lang.switch": "切换语言",
    "skip.main": "跳转到主内容",

    "status.ready": "系统就绪，请登录并开始图编排对话。",
    "status.custom": ({ text }) => String(text),
    "status.signingIn": "正在登录...",
    "status.loginFailed": ({ reason }) => `登录失败：${reason}`,
    "status.signedIn": ({ roles }) => `登录成功，角色：${roles}。`,
    "status.userRegistered": "用户注册成功，可直接登录。",
    "status.registerFailed": ({ reason }) => `注册失败：${reason}`,
    "status.signedOut": "已退出登录。",
    "status.healthPassed": ({ time }) => `健康检查通过，时间：${time}。`,
    "status.healthFailed": ({ reason }) => `健康检查失败：${reason}`,
    "status.graphInterrupted": "图流程请求中断确认。",
    "status.graphReady": "助手已返回结果。",
    "status.graphFailed": ({ reason }) => `图执行失败：${reason}`,
    "status.usersLoaded": ({ count }) => `已加载 ${count} 个用户。`,
    "status.usersFailed": ({ reason }) => `加载用户失败：${reason}`,
    "status.sessionExpired": ({ reason }) => `会话失效：${reason}`,

    "hero.overline": "Tripy 企业控制台",
    "hero.title": "面向生产治理的图编排旅行助手。",
    "hero.copy": "提供安全认证、RBAC、可观测后端与实时操作台，支撑关键业务流程。",

    "env.title": "环境",
    "env.snapshot": "系统快照",
    "env.apiBase": "API 地址",
    "env.live": "存活",
    "env.ready": "就绪",
    "env.checked": "检查时间",
    "env.runHealth": "执行健康检查",
    "env.checking": "检查中...",

    "session.title": "会话",
    "session.authed": "已认证",
    "session.guest": "访客",
    "session.username": "用户名",
    "session.password": "密码",
    "session.signIn": "登录",
    "session.signOut": "退出",

    "register.title": "创建用户",
    "register.username": "用户名",
    "register.password": "密码",
    "register.passenger": "乘客 ID（可选）",
    "register.submit": "注册",
    "register.creating": "创建中...",

    "workspace.title": "工作区",
    "view.assistant": "图助手",
    "view.assistantDesc": "线程化旅行流程",
    "view.identity": "身份",
    "view.identityDesc": "角色与权限",
    "view.admin": "管理",
    "view.adminDesc": "用户清单",
    "view.system": "系统",
    "view.systemDesc": "健康与配置",

    "assistant.title": "图助手",
    "assistant.thread": "线程",
    "assistant.newThread": "新建",
    "assistant.tip": "可在输入框使用 Cmd/Ctrl + Enter 快速发送。",
    "assistant.noPermission": "当前用户缺少 graph:execute 权限。",
    "assistant.placeholder": "请输入旅行相关任务，让 Tripy 进行规划或推理...",
    "assistant.send": "发送",
    "assistant.sending": "图执行中...",
    "assistant.clear": "清空线程",
    "assistant.emptyTitle": "暂无对话",
    "assistant.emptyDesc": "可以先输入改签、政策检查、路线建议等请求。",
    "assistant.interrupted": "流程中断",

    "identity.title": "身份与 RBAC",
    "identity.notSigned": "未登录",
    "identity.prompt": "登录后可查看 RBAC 声明。",
    "identity.profile": "个人信息",
    "identity.userId": "用户 ID",
    "identity.passengerId": "乘客 ID",
    "identity.email": "邮箱",
    "identity.userStatus": "状态",
    "identity.active": "启用",
    "identity.disabled": "停用",
    "identity.roles": "角色",
    "identity.permissions": "权限",
    "identity.none": "无",

    "admin.title": "管理用户",
    "admin.refresh": "刷新用户",
    "admin.loading": "加载中...",
    "admin.noPermission": "缺少 users:read 权限，无法读取管理列表。",
    "admin.signInPrompt": "请先登录再访问管理接口。",
    "admin.id": "ID",
    "admin.username": "用户名",
    "admin.roles": "角色",
    "admin.permissions": "权限",
    "admin.empty": "尚未加载用户。",

    "system.title": "系统控制台",
    "system.connection": "连接",
    "system.session": "会话",
    "system.activity": "活动",
    "system.api": "API",
    "system.authenticated": "已认证",
    "system.yes": "是",
    "system.no": "否",
    "system.roles": "角色",
    "system.permissions": "权限数",
    "system.messages": "消息数",
    "system.thread": "线程"
  }
};

export const detectLocale = (): Locale => {
  if (typeof navigator === "undefined") {
    return "en";
  }
  return navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
};

export const t = (
  locale: Locale,
  key: string,
  params: Record<string, Primitive> = {}
): string => {
  const localized = messages[locale][key] ?? messages.en[key] ?? key;
  if (typeof localized === "function") {
    return localized(params);
  }
  return localized;
};
