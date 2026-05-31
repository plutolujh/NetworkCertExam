/**
 * Cloudflare Worker with D1 Database
 * API Router for 网络规划师备考 - 每日练习系统
 */

// 知识点速记表
const knowledgeCards = {
  'TCP三次握手': {
    principle: '三次握手建立TCP连接',
    steps: ['客户端发送SYN=x', '服务器返回SYN+ACK=y, ack=x+1', '客户端发送ACK=x+1, ack=y+1'],
    state: 'CLOSED→SYN_SENT→ESTABLISHED (客户端)',
    mnemonic: '主动方先SYN，被动方SYN+ACK，然后ACK确认'
  },
  'VLAN': {
    principle: '隔离广播域，划分逻辑网络',
    types: '基于端口(最常用)、基于MAC、基于协议、基于IP子网',
    trunk: '802.1Q打标签，4字节',
    mnemonic: 'VLAN隔离广播，Trunk承载多VLAN'
  },
  'STP': {
    principle: '生成树协议，消除环路',
    states: 'Blocking→Listening→Learning→Forwarding',
    roles: '根桥、根端口、指定端口、非指定端口',
    mnemonic: '先选根桥，再定端口角色'
  }
};

// 获取随机题目
async function getRandomQuestion(db, category) {
  let query = 'SELECT * FROM questions';
  let bindings = [];
  if (category) {
    query += ' WHERE category LIKE ?';
    bindings.push(`%${category}%`);
  }
  query += ' ORDER BY RANDOM() LIMIT 1';
  const result = await db.prepare(query).bind(...bindings).first();
  return result;
}

// 获取每日一题
async function getDailyQuestion(db, date) {
  // 按日期hash选择题目，确保每天同一日期得到相同题目
  const hash = date.split('-').join('');
  const num = parseInt(hash) % 757; // 757是题库总数
  const result = await db.prepare('SELECT * FROM questions LIMIT 1 OFFSET ?').bind(num).first();
  return result;
}

// 评判答案
function checkAnswer(question, userAnswer) {
  const correct = question.answer.toString().split(',');
  const user = userAnswer.toString().split(',');

  if (correct.length !== user.length) return false;

  const correctSet = new Set(correct.map(x => x.trim()));
  const userSet = new Set(user.map(x => x.trim()));

  if (correctSet.size !== userSet.size) return false;

  for (const c of correctSet) {
    if (!userSet.has(c)) return false;
  }
  return true;
}

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

      // ===== 题库API =====

      // 获取知识点速记卡
      if (path === '/api/knowledge') {
        const tag = url.searchParams.get('tag') || 'TCP';
        const card = knowledgeCards[tag];
        if (card) {
          return new Response(JSON.stringify({ tag, ...card }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }
        // 返回所有标签
        return new Response(JSON.stringify({ tags: Object.keys(knowledgeCards) }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // 获取随机一题
      if (path === '/api/question/random') {
        const category = url.searchParams.get('category');
        const question = await getRandomQuestion(db, category);
        if (!question) {
          return new Response(JSON.stringify({ error: '题库为空' }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }
        // 不返回正确答案
        const { answer, ...safeQuestion } = question;
        return new Response(JSON.stringify(safeQuestion), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // 获取每日一题
      if (path === '/api/question/daily') {
        const date = url.searchParams.get('date') || new Date().toISOString().split('T')[0];
        const question = await getDailyQuestion(db, date);
        if (!question) {
          return new Response(JSON.stringify({ error: '题库为空' }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }
        const { answer, ...safeQuestion } = question;
        return new Response(JSON.stringify(safeQuestion), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // 提交答案评判
      if (path === '/api/question/submit' && request.method === 'POST') {
        const body = await request.json();
        const { question_id, user_answer, is_correct } = body;

        // 获取题目答案和解析
        const question = await db.prepare('SELECT answer, explanation FROM questions WHERE id = ?').bind(question_id).first();

        // 记录答题历史
        await db.prepare(`
          INSERT INTO question_history (question_id, user_answer, is_correct, answered_at)
          VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        `).bind(question_id, user_answer, is_correct ? 1 : 0).run();

        // 如果答错，记录到错题本
        if (!is_correct) {
          await db.prepare(`
            INSERT OR IGNORE INTO wrong_questions (question_id, count, last_reviewed)
            VALUES (?, 1, CURRENT_TIMESTAMP)
          `).bind(question_id).run();
        } else {
          // 答对了，从错题本移除
          await db.prepare('DELETE FROM wrong_questions WHERE question_id = ?').bind(question_id).run();
        }

        return new Response(JSON.stringify({
          status: 'recorded',
          answer: question?.answer,
          explanation: question?.explanation
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // 获取错题本
      if (path === '/api/wrong-questions') {
        const { results } = await db.prepare(`
          SELECT q.*, w.count, w.last_reviewed
          FROM wrong_questions w
          JOIN questions q ON w.question_id = q.id
          ORDER BY w.count DESC
        `).all();
        return new Response(JSON.stringify(results), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // 获取答题统计
      if (path === '/api/stats') {
        const total = await db.prepare('SELECT COUNT(*) as cnt FROM questions').first();
        const answered = await db.prepare('SELECT COUNT(DISTINCT question_id) as cnt FROM question_history').first();
        const correct = await db.prepare('SELECT COUNT(*) as cnt FROM question_history WHERE is_correct = 1').first();
        const wrongCount = await db.prepare('SELECT COUNT(*) as cnt FROM wrong_questions').first();

        return new Response(JSON.stringify({
          total: total?.cnt || 0,
          answered: answered?.cnt || 0,
          correct: correct?.cnt || 0,
          wrongCount: wrongCount?.cnt || 0,
          accuracy: answered?.cnt > 0 ? Math.round(correct?.cnt / answered?.cnt * 100) : 0
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // ===== 原有API保持兼容 =====

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