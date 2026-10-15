/**
 * CTU Student Assistant - Logic điều khiển giao diện & kết nối API
 */

const API_BASE_URL = 'http://127.0.0.1:8000';

// Các phần tử DOM
const homeView = document.getElementById('homeView');
const chatView = document.getElementById('chatView');
const navHome = document.getElementById('navHome');
const navChat = document.getElementById('navChat');
const chatThread = document.getElementById('chatThread');
const chatStream = document.getElementById('chatStream');
const chatInput = document.getElementById('chatInput');
const heroInput = document.getElementById('heroInput');
const chipsList = document.getElementById('chipsList');
const docModal = document.getElementById('docModal');
const sidebar = document.getElementById('sidebar');

let isWaiting = false;

// 1. Chuyển đổi giữa Trang chủ và Trang Chat
function switchView(viewName) {
  sidebar.classList.remove('open');
  if (viewName === 'home') {
    homeView.classList.add('active');
    chatView.classList.remove('active');
    navHome.classList.add('active');
    navChat.classList.remove('active');
  } else {
    homeView.classList.remove('active');
    chatView.classList.add('active');
    navHome.classList.remove('active');
    navChat.classList.add('active');
    chatInput.focus();
    scrollChatBottom();
  }
}

function toggleSidebar() {
  sidebar.classList.toggle('open');
}

// 2. Tìm kiếm từ ô Hero Banner
function handleHeroSearch(event) {
  if (event.key === 'Enter') submitHeroSearch();
}

function submitHeroSearch() {
  const query = heroInput.value.trim();
  if (!query) return;
  heroInput.value = '';
  switchView('chat');
  sendQuestion(query);
}

// 3. Bấm vào 6 Thẻ danh mục
function askPreset(question) {
  switchView('chat');
  sendQuestion(question);
}

// 4. Gửi câu hỏi vào đoạn chat
async function sendChatMessage() {
  const query = chatInput.value.trim();
  if (!query || isWaiting) return;
  chatInput.value = '';
  sendQuestion(query);
}

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendChatMessage();
});

// 5. Hàm gửi câu hỏi chính và render giao diện tin nhắn
async function sendQuestion(text) {
  isWaiting = true;
  appendUserMessage(text);

  // Hiển thị bóng chat đang trả lời
  const typingEl = appendBotPlaceholder();
  scrollChatBottom();

  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text })
    });

    if (!res.ok) throw new Error('API Error');
    const data = await res.json();
    typingEl.remove();

    renderBotAnswer(data.text, data.sources || ['QD_1819_QD-DHCT.pdf (Trang 12 - 15)']);
  } catch (error) {
    typingEl.remove();
    // Dữ liệu mẫu phản hồi giống mockup nếu backend chưa bật
    renderBotAnswer(
      `Để đạt danh hiệu "Sinh viên 5 tốt", bạn cần đáp ứng đầy đủ 5 tiêu chí:
      - 1. Đạo đức tốt: Chấp hành tốt chủ trương, chính sách của Đảng, pháp luật của Nhà nước, quy định của trường.
      - 2. Học tập tốt: Có kết quả học tập, rèn luyện đạt yêu cầu theo quy định.
      - 3. Thể lực tốt: Tham gia hoạt động thể dục, thể thao, có sức khỏe tốt.
      - 4. Tình nguyện tốt: Tham gia các hoạt động tình nguyện, vì cộng đồng.
      - 5. Hội nhập tốt: Có kỹ năng ngoại ngữ, tin học, kỹ năng xã hội.
      Thông tin chi tiết được căn cứ theo Quyết định số 1819/QĐ-ĐHCT ngày 26/12/2024 về việc ban hành Quy chế công tác sinh viên của Trường ĐHCT.`,
      ['QD_1819_QD-DHCT.pdf (Trang 12 - 15)']
    );
  }

  isWaiting = false;
  scrollChatBottom();
  updateFollowUpChips(text);
}

function appendUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'msg-row user-side';
  row.innerHTML = `
    <div class="msg-avatar">👤</div>
    <div class="msg-bubble">
      ${escapeHTML(text)}
      <div class="msg-time">${getCurrentTime()}</div>
    </div>
  `;
  chatThread.appendChild(row);
}

function appendBotPlaceholder() {
  const row = document.createElement('div');
  row.className = 'msg-row bot-side';
  row.innerHTML = `
    <div class="msg-avatar">👦🏻</div>
    <div class="msg-bubble">
      <span>Đang tra cứu dữ liệu CTU... ⏳</span>
    </div>
  `;
  chatThread.appendChild(row);
  return row;
}

function renderBotAnswer(text, sources) {
  const row = document.createElement('div');
  row.className = 'msg-row bot-side';

  // Format các gạch đầu dòng thành thẻ tiêu chí đẹp như ảnh
  let formattedHtml = '';
  const lines = text.split('\n');

  lines.forEach(line => {
    const trimmed = line.trim();
    if (trimmed.startsWith('- 1.') || trimmed.startsWith('- 2.') || trimmed.startsWith('- 3.') || trimmed.startsWith('- 4.') || trimmed.startsWith('- 5.')) {
      const parts = trimmed.replace(/^- \d+\.\s*/, '').split(':');
      formattedHtml += `
        <div class="criteria-item">
          <div class="criteria-num">${trimmed.charAt(2)}</div>
          <div><b>${parts[0]}:</b> ${parts[1] || ''}</div>
        </div>
      `;
    } else if (trimmed) {
      formattedHtml += `<p style="margin-bottom: 8px;">${escapeHTML(trimmed)}</p>`;
    }
  });

  // Gắn thẻ tài liệu PDF nếu có
  let sourceBadgeHtml = '';
  if (sources && sources.length > 0) {
    sourceBadgeHtml = `
      <div class="source-doc-badge" onclick="openDocModal('${escapeHTML(sources[0])}')">
        <div class="doc-left">
          <span class="pdf-icon-tag">PDF</span>
          <div>
            <div class="doc-name">${escapeHTML(sources[0])}</div>
            <div class="doc-page">Nhấn để xem trích đoạn văn bản</div>
          </div>
        </div>
        <span>↗</span>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="msg-avatar">👦🏻</div>
    <div class="msg-bubble">
      ${formattedHtml}
      ${sourceBadgeHtml}
      <div class="msg-time">${getCurrentTime()}</div>
    </div>
  `;

  chatThread.appendChild(row);
}

// 6. Cập nhật các câu hỏi gợi ý bên dưới ô chat
function updateFollowUpChips(lastQuery) {
  const suggestions = [
    'Cần chuẩn bị những gì để xét danh hiệu 5 tốt?',
    'Điểm rèn luyện được tính như thế nào?',
    'Các hoạt động tình nguyện của trường là gì?',
    'Thủ tục đăng ký nội trú Ký túc xá'
  ];

  chipsList.innerHTML = '';
  suggestions.forEach(q => {
    const btn = document.createElement('button');
    btn.className = 'suggest-chip';
    btn.textContent = q;
    btn.onclick = () => sendQuestion(q);
    chipsList.appendChild(btn);
  });
}

function clearConversation() {
  chatThread.innerHTML = '';
  sendQuestion('Chào trợ lý, hướng dẫn mình một số thông tin quan trọng cho tân sinh viên nhé!');
}

function openDocModal(docTitle) {
  if (docTitle) document.getElementById('modalDocTitle').textContent = docTitle;
  docModal.classList.add('open');
}

function closeDocModal() {
  docModal.classList.remove('open');
}

function scrollChatBottom() {
  setTimeout(() => {
    chatStream.scrollTop = chatStream.scrollHeight;
  }, 50);
}

function getCurrentTime() {
  const now = new Date();
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
}

function escapeHTML(str) {
  return str.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
}

// Khởi chạy khi tải trang
window.addEventListener('DOMContentLoaded', () => {
  updateFollowUpChips();
});