/**
 * Cloudflare Worker with D1 Database
 * API Router for 网络规划师备考
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

    const db = env.DB;

    try {
      // 健康检查
      if (path === '/api/health') {
        return new Response(JSON.stringify({ status: 'ok' }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // 测试 D1 连接
      if (path === '/api/test-d1') {
        const result = await db.prepare('SELECT 1 as test').first();
        return new Response(JSON.stringify({ success: true, d1: result }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // 获取每日内容
      if (path === '/api/daily') {
        const date = url.searchParams.get('date') || new Date().toISOString().split('T')[0];
        const result = await db.prepare('SELECT * FROM daily_content WHERE date = ?').bind(date).first();

        if (!result) {
          return new Response(JSON.stringify({
            date: date,
            type: 'comprehensive',
            topic: '综合知识 - 自助学习',
            tags: '选择题,高频考点',
            knowledge: JSON.stringify([
              { title: 'TCP三次握手', points: ['第一次：SYN=1, seq=x', '第二次：SYN=1, ACK=1, seq=y, ack=x+1', '第三次：ACK=1, seq=x+1, ack=y+1'] },
              { title: 'VLAN划分', points: ['基于端口（最常用）', '基于MAC地址', '基于协议', '基于IP子网'] }
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
      if (path === '/api/progress' && request.method === 'POST') {
        const body = await request.json();
        await db.prepare(`
          INSERT INTO learning_progress (date, task_type, status, score, notes, updated_at)
          VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        `).bind(body.date, body.task_type, body.status, body.score || null, body.notes || null).run();

        return new Response(JSON.stringify({ status: 'updated' }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // 获取学习进度
      if (path === '/api/progress') {
        const date = url.searchParams.get('date');
        let query = 'SELECT * FROM learning_progress';
        let bindings = [];
        if (date) {
          query += ' WHERE date = ?';
          bindings.push(date);
        }
        const { results } = await db.prepare(query).bind(...bindings).all();
        return new Response(JSON.stringify(results), {
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