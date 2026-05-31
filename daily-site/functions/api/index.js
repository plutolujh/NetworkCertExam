/**
 * Cloudflare Worker API for 网络规划师备考
 * 数据库: networkcert-daily (D1 SQLite)
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // 初始化数据库表
      if (path === '/api/init') {
        return await handleInit(env, corsHeaders);
      }

      // 获取每日内容
      if (path === '/api/daily' && request.method === 'GET') {
        return await handleGetDaily(env, url, corsHeaders);
      }

      // 更新学习进度
      if (path === '/api/progress' && request.method === 'POST') {
        return await handleUpdateProgress(env, request, corsHeaders);
      }

      // 获取学习进度
      if (path === '/api/progress' && request.method === 'GET') {
        return await handleGetProgress(env, url, corsHeaders);
      }

      // 获取薄弱点
      if (path === '/api/weak-points' && request.method === 'GET') {
        return await handleGetWeakPoints(env, corsHeaders);
      }

      // 添加薄弱点
      if (path === '/api/weak-points' && request.method === 'POST') {
        return await handleAddWeakPoint(env, request, corsHeaders);
      }

      // 健康检查
      if (path === '/api/health') {
        return new Response(JSON.stringify({ status: 'ok' }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      return new Response('Not Found', { status: 404 });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};

// 初始化数据库表
async function handleInit(env, corsHeaders) {
  const schema = `
    CREATE TABLE IF NOT EXISTS daily_content (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL UNIQUE,
      type TEXT NOT NULL,
      topic TEXT NOT NULL,
      tags TEXT,
      knowledge TEXT NOT NULL,
      framework TEXT,
      essay_outline TEXT,
      essay_template TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS learning_progress (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL,
      task_type TEXT NOT NULL,
      status TEXT DEFAULT 'pending',
      score INTEGER,
      notes TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS weak_points (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      topic TEXT NOT NULL,
      category TEXT NOT NULL,
      difficulty INTEGER DEFAULT 3,
      practice_count INTEGER DEFAULT 0,
      last_practiced TEXT,
      next_review TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_settings (
      id INTEGER PRIMARY KEY,
      exam_date TEXT DEFAULT '2026-11-14',
      daily_goal INTEGER DEFAULT 3,
      study_mode TEXT DEFAULT 'normal',
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
  `;

  // 执行建表SQL
  await env.DB.exec(schema);

  // 检查是否已有数据
  const { results } = await env.DB.prepare('SELECT COUNT(*) as count FROM daily_content').all();

  // 如果没有数据，插入初始内容
  if (results[0].count === 0) {
    await seedInitialData(env);
  }

  return new Response(JSON.stringify({ status: 'initialized' }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// 插入初始数据
async function seedInitialData(env) {
  // 案例分析内容 (6月份)
  const caseData = [
    {
      date: '2026-06-01',
      type: 'case',
      topic: '第一题：网络系统规划设计与优化',
      tags: 'SDN,无线网络,负载均衡',
      knowledge: JSON.stringify([
        { title: 'SDN控制器作用', points: ['网络可编程配置自动化', '流量调度灵活优化带宽', '故障快速响应自动恢复', '统一管控简化运维'] },
        { title: '无线网络部署关键因素', points: ['覆盖范围和信号强度', '接入容量和并发用户数', '信道规划和干扰规避', '终端兼容性', '安全策略Portal/802.1X'] },
        { title: '出口负载均衡策略', points: ['基于目的地址的策略路由', '教育网地址段走教育网出口', '其他流量默认走运营商出口'] }
      ]),
      framework: JSON.stringify([
        '【问题1】优化措施：SDN控制器集中管控、无线AP补盲、多出口负载均衡、VLAN标准化、自动化运维',
        '【问题2】SDN部署位置：核心层或独立集中部署；改进作用：可编程、流量调度、故障恢复、统一管控',
        '【问题3】无线部署因素：覆盖范围、接入容量、信道规划、干扰规避、终端兼容、安全策略',
        '【问题4】出口负载均衡：策略路由基于目的地址，教育网走教育网出口，其他走运营商出口'
      ])
    },
    {
      date: '2026-06-02',
      type: 'case',
      topic: '第二题：网络安全防护方案设计',
      tags: '防火墙,IDS,VPN,ACL,态势感知',
      knowledge: JSON.stringify([
        { title: '防火墙部署与作用', points: ['防火墙1：互联网与DMZ之间边界防护', '防火墙2：DMZ与内网之间分区隔离', '防火墙是主动防御主动阻止'] },
        { title: 'IDS入侵检测系统', points: ['旁路部署不影响网络性能', '特征库匹配检测已知攻击', '行为分析检测异常流量', '优点可双向检测，缺点无法主动阻断'] },
        { title: 'VPN技术对比', points: ['SSL VPN：移动办公Web应用远程接入仅需浏览器', 'IPSec VPN：Site-to-Site固定场所互联需专业客户端', '记忆口诀：移动办公用SSL站点互联用IPSec'] }
      ]),
      framework: JSON.stringify([
        '【问题1】防火墙1：互联网-DMZ边界防护；防火墙2：DMZ-内网分区隔离；IDS：旁路入侵检测；VPN：远程接入加密',
        '【问题2】态势感知平台核心功能：全网安全事件采集、威胁检测预警、资产可视化、应急响应联动、态势预测',
        '【问题3】ACL工作原理：按规则顺序匹配，匹配即执行，未匹配隐含deny。示例：permit tcp 10.1.0.0 0.0.255.255 10.2.0.0 0.0.255.255 eq 80',
        '【问题4】VPN应用场景：远程移动办公、总部分支机构互联、第三方人员接入。SSL VPN适合移动办公，IPSec VPN适合Site-to-Site'
      ])
    },
    {
      date: '2026-06-03',
      type: 'case',
      topic: '第三题：传输网络规划与设计',
      tags: 'SDH,MSTP,OTN,DWDM,环形保护',
      knowledge: JSON.stringify([
        { title: '传输技术对比', points: ['SDH：同步数字体系，成熟可靠，用于语音业务', 'MSTP：多业务传送平台，在SDH上集成以太网', 'OTN：光传送网，大容量智能光交换，支持多种业务', 'DWDM：密集波分复用，极高容量用于骨干网'] },
        { title: 'OTN主要优势', points: ['大带宽：单波长可达100G甚至更高', '业务适配性：支持SDH/以太网/视频多种业务', '智能光交换：波长路由动态分配', '高可靠性：光环保护'] },
        { title: '环形保护方式', points: ['通道保护环：业务双发双收，倒换时间小于50ms', '复用段保护环：利用K1/K2字节倒换，倒换时间小于50ms', '区别：通道保护面向业务，复用段保护面向链路'] }
      ]),
      framework: JSON.stringify([
        '【问题1】技术对比：SDH成熟可靠用于语音，MSTP集成以太网，OTN大容量智能，DWDM极高容量骨干。OTN优势：大带宽、多业务适配、智能光交换',
        '【问题2】通道保护环：业务双发双收，倒换快；复用段保护环：利用K1/K2倒换，链路级别。适用场景：通道保护适合话音业务，复用段保护适合数据业务',
        '【问题3】可靠性设计：设备冗余双主控双电源、链路冗余双上联、网络拓扑环形组网、自动倒换',
        '【问题4】推荐方案：从技术成熟度和兼容性角度，MSTP或OTN均可支持多业务。推荐OTN，因其支持SDH/以太网/视频且扩展性好'
      ])
    }
  ];

  // 综合知识内容
  const comprehensiveData = [
    {
      date: '2026-06-04',
      type: 'comprehensive',
      topic: '综合知识 - 计算机网络基础',
      tags: 'OSI,TCP/IP,协议',
      knowledge: JSON.stringify([
        { title: 'OSI七层模型', points: ['物理层：比特传输', '数据链路层：帧传输，MAC地址', '网络层：路由选择，IP协议', '传输层：端到端，TCP/UDP', '会话层：会话管理', '表示层：数据格式', '应用层：HTTP、FTP、SMTP'] },
        { title: 'TCP三次握手', points: ['第一次：SYN=1, seq=x', '第二次：SYN=1, ACK=1, seq=y, ack=x+1', '第三次：ACK=1, seq=x+1, ack=y+1'] },
        { title: 'UDP特性', points: ['无连接，不建立会话', '不可靠交付', '高效低延迟', '用于DNS、DHCP、实时音视频'] }
      ]),
      framework: null,
      essay_outline: null,
      essay_template: null
    }
  ];

  // 插入数据
  for (const item of [...caseData, ...comprehensiveData]) {
    await env.DB.prepare(`
      INSERT INTO daily_content (date, type, topic, tags, knowledge, framework, essay_outline, essay_template)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(item.date, item.type, item.topic, item.tags, item.knowledge, item.framework, item.essay_outline, item.essay_template).run();
  }
}

// 获取每日内容
async function handleGetDaily(env, url, corsHeaders) {
  const date = url.searchParams.get('date') || new Date().toISOString().split('T')[0];

  const result = await env.DB.prepare(`
    SELECT * FROM daily_content WHERE date = ?
  `).bind(date).first();

  if (!result) {
    // 如果没有特定日期的数据，返回通用内容
    return new Response(JSON.stringify({
      date: date,
      type: 'comprehensive',
      topic: '综合知识 - 自助学习',
      tags: '选择题,高频考点',
      knowledge: JSON.stringify([
        { title: 'TCP三次握手', points: ['第一次：SYN=1, seq=x', '第二次：SYN=1, ACK=1, seq=y, ack=x+1', '第三次：ACK=1, seq=x+1, ack=y+1'] },
        { title: 'VLAN划分', points: ['基于端口（最常用）', '基于MAC地址', '基于协议', '基于IP子网'] },
        { title: 'STP生成树协议', points: ['防止网络环路', '选举根桥', '阻塞非根端口', '快速收敛用RSTP/MSTP'] }
      ]),
      framework: null
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  return new Response(JSON.stringify(result), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// 更新学习进度
async function handleUpdateProgress(env, request, corsHeaders) {
  const body = await request.json();
  const { date, task_type, status, score, notes } = body;

  await env.DB.prepare(`
    INSERT INTO learning_progress (date, task_type, status, score, notes, updated_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(date, task_type) DO UPDATE SET
      status = excluded.status,
      score = excluded.score,
      notes = excluded.notes,
      updated_at = CURRENT_TIMESTAMP
  `).bind(date, task_type, status, score, notes).run();

  return new Response(JSON.stringify({ status: 'updated' }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// 获取学习进度
async function handleGetProgress(env, url, corsHeaders) {
  const date = url.searchParams.get('date');

  let query = 'SELECT * FROM learning_progress';
  let bindings = [];

  if (date) {
    query += ' WHERE date = ?';
    bindings.push(date);
  }

  query += ' ORDER BY date DESC, task_type ASC';

  const { results } = await env.DB.prepare(query).bind(...bindings).all();

  return new Response(JSON.stringify(results), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// 获取薄弱点
async function handleGetWeakPoints(env, corsHeaders) {
  const { results } = await env.DB.prepare(`
    SELECT * FROM weak_points ORDER BY difficulty DESC, practice_count ASC
  `).all();

  return new Response(JSON.stringify(results), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// 添加薄弱点
async function handleAddWeakPoint(env, request, corsHeaders) {
  const body = await request.json();
  const { topic, category, difficulty } = body;

  const result = await env.DB.prepare(`
    INSERT INTO weak_points (topic, category, difficulty)
    VALUES (?, ?, ?)
  `).bind(topic, category, difficulty || 3).run();

  return new Response(JSON.stringify({ status: 'added', id: result.meta.last_row_id }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}