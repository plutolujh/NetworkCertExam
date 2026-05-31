# Cloudflare Pages + Workers 部署问题汇总

## 问题1：API Token 权限不足

**错误信息：**
```
Authentication error [code: 10000]
```

**原因：** 使用的是 User API Token，不是 Account API Token。

**解决：**
1. 创建 Account API Token（不是 User Token）
2. 需要权限：Workers Scripts Read/Write、D1 Read/Write、Pages Read/Write
3. Token 格式：`cfat_` 开头

---

## 问题2：Pages Functions 无法绑定 D1

**错误信息：**
```
Error 1019: Compute server error
```

**原因：** Cloudflare Pages Functions 的 D1 绑定有 bug 或限制，env.DB 返回 undefined。

**解决：**
- 改用独立 Worker 托管静态文件 + API
- Worker 使用 `assets` 配置托管静态文件
- 用 Worker 绑定 D1（正常工作）

---

## 问题3：wrangler.jsonc 的 assets 配置格式错误

**错误信息：**
```
"assets" should be an object, but got value "assets" of type string
```

**原因：** `assets` 配置格式不对。

**正确格式：**
```json
{
  "assets": {
    "directory": "."
  }
}
```

不是 `assets: "."`

---

## 问题4：wrangler deploy 在 Pages 项目中执行

**错误信息：**
```
It looks like you've run a Workers-specific command in a Pages project.
For Pages, please run `wrangler pages deploy` instead.
```

**原因：** Wrangler 检测到 wrangler.jsonc 认为这是 Pages 项目。

**解决：**
- 如果用 Workers + Assets，用 `wrangler deploy`
- 如果用 Pages，用 `wrangler pages deploy .`
- 两个命令不要混用

---

## 问题5：GitHub Push 被 Secret Scanner 拦截

**错误信息：**
```
remote: Push cannot contain secrets
```

**原因：** .env 文件被推送到 GitHub。

**解决：**
1. 从 Git 历史中删除： `git filter-branch --force --index-filter 'git rm -rf --cached --ignore-unmatch .env' --tag-name-filter cat -- --all`
2. 添加入 .gitignore：`.env*`
3. Force push: `git push origin main --force`

---

## 问题6：Cloudflare Pages Build/Deploy Command 配置

**背景：** Pages 项目可以配置 Build command 和 Deploy command。

**正确配置：**
- **Build command:** 留空（Worker 项目不需要构建）
- **Deploy command:** `npx wrangler deploy`（如果用 Pages 的 CI/CD）

**注意：** 如果用 GitHub Actions 部署 Worker，不需要配置这两个命令，在 Actions workflow 中处理。

---

## 正确架构（最终方案）

```
networkcert-daily/
├── src/index.js       # Worker API 入口
├── index.html         # 静态页面
├── manifest.json      # PWA manifest
├── wrangler.jsonc     # Wrangler 配置
│   └── assets + D1 绑定
└── .github/workflows/deploy.yml  # CI/CD
```

**部署结果：**
- 页面：`https://networkcert-daily.plutolu.workers.dev/`
- API：`https://networkcert-daily.plutolu.workers.dev/api/*`

**wrangler.jsonc 示例：**
```json
{
  "name": "networkcert-daily",
  "main": "src/index.js",
  "assets": {
    "directory": "."
  },
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "networkcert-daily",
      "database_id": "d932e501-8d69-423e-a6a8-86b9f2b3ae74"
    }
  ]
}
```

---

## 常用命令

```bash
# 本地开发
wrangler dev

# 部署
wrangler deploy

# 干跑测试
wrangler deploy --dry-run

# 查看 D1 数据
wrangler d1 execute networkcert-daily --local --file=schema.sql

# 查看 Worker 日志
wrangler tail
```