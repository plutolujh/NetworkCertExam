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

    // 健康检查
    if (path === '/api/health') {
      return new Response(JSON.stringify({ status: 'ok', message: 'Worker is running' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // 测试 D1 连接
    if (path === '/api/test-d1') {
      try {
        const result = await env.DB.prepare('SELECT 1 as test').first();
        return new Response(JSON.stringify({ success: true, d1: result }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } catch (err) {
        return new Response(JSON.stringify({ success: false, error: err.message }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    // 获取每日内容
    if (path === '/api/daily') {
      const date = url.searchParams.get('date') || new Date().toISOString().split('T')[0];
      try {
        const result = await env.DB.prepare('SELECT * FROM daily_content WHERE date = ?').bind(date).first();
        if (!result) {
          return new Response(JSON.stringify({
            date: date,
            type: 'comprehensive',
            topic: '综合知识 - 自助学习',
            knowledge: JSON.stringify([
              { title: 'TCP三次握手', points: ['第一次：SYN=1, seq=x', '第二次：SYN=1, ACK=1, seq=y, ack=x+1'] },
              { title: 'VLAN划分', points: ['基于端口（最常用）', '基于MAC地址'] }
            ])
          }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
        }
        return new Response(JSON.stringify(result), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    return new Response('Not Found', { status: 404 });
  }
};