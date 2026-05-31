# 网络规划师备考网站 - Cloudflare Pages 部署

## 部署步骤

### 1. 获取 D1 数据库 ID

登录 [Cloudflare Dashboard](https://dash.cloudflare.com) → Workers & Pages → D1 → networkcert-daily → 右侧可见 "Database ID"

### 2. 更新 wrangler.toml

将 `wrangler.toml` 中的 `database_id` 替换为你的实际 ID：

```toml
[[d1_databases]]
binding = "DB"
database_name = "networkcert-daily"
database_id = "替换为你的实际数据库ID"
```

### 3. 部署到 Cloudflare Pages

```bash
cd daily-site

# 登录 Cloudflare
npx wrangler pages project create networkcert-daily

# 部署
npx wrangler pages deploy . --project-name=networkcert-daily
```

或者通过 Git 推送后，Cloudflare 会自动部署。

### 4. 初始化数据库

部署完成后，访问以下 URL 初始化数据库和初始数据：

```
https://network-daily.plutolu.workers.dev/api/init
```

返回 `{"status":"initialized"}` 即成功。

---

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/init` | POST | 初始化数据库（创建表、插入初始数据） |
| `/api/daily?date=2026-06-01` | GET | 获取指定日期的学习内容 |
| `/api/progress` | GET | 获取学习进度 |
| `/api/progress` | POST | 更新学习进度 |
| `/api/weak-points` | GET | 获取薄弱点 |
| `/api/weak-points` | POST | 添加薄弱点 |

---

## 功能

- ✅ 每日学习内容（从数据库读取）
- ✅ 学习进度追踪
- ✅ 薄弱点记录
- ✅ 考前倒计时
- ✅ 前后日期导航

---

## 文件结构

```
daily-site/
├── index.html           # 前端页面
├── manifest.json         # PWA 配置
├── wrangler.toml        # Cloudflare 配置
├── schema.sql          # 数据库 Schema
├── functions/
│   └── api/
│       └── index.js    # API Worker
└── DEPLOY.md          # 部署指南
```