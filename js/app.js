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

  // Dùng marked.parse để render đầy đủ in đậm, danh sách gạch đầu dòng, bảng...
  let formattedHtml = '';
  if (typeof marked !== 'undefined') {
    formattedHtml = marked.parse(text);
  } else {
    formattedHtml = `<p>${escapeHTML(text).replace(/\n/g, '<br>')}</p>`;
  }


  // Gắn thẻ tài liệu tham chiếu nếu có
  let sourceBadgeHtml = '';
  if (sources && sources.length > 0) {
    const firstSrc = sources[0];
    const fileName = typeof firstSrc === 'object' ? (firstSrc.file || 'Tài liệu CTU') : firstSrc;
    const excerpt = typeof firstSrc === 'object' ? (firstSrc.excerpt || '') : '';
    const dlUrl = typeof firstSrc === 'object' && firstSrc.download_url ? `${API_BASE_URL}${firstSrc.download_url}` : '#';
    const ext = fileName.split('.').pop().toUpperCase();
    const tagClass = ext === 'DOCX' ? 'docx-icon-tag' : (ext === 'XLSX' ? 'xlsx-icon-tag' : 'pdf-icon-tag');

    sourceBadgeHtml = `
      <div class="source-doc-badge">
        <div class="doc-left" onclick="showExcerptModal('${escapeHTML(fileName)}', '${escapeHTML(excerpt)}')">
          <span class="${tagClass}">${ext}</span>
          <div class="doc-info">
            <div class="doc-name" title="${escapeHTML(fileName)}">${escapeHTML(fileName)}</div>
            <div class="doc-page">Nhấn để xem trích đoạn văn bản</div>
          </div>
        </div>
        <div class="doc-actions">
          <a class="btn-badge-download" href="${dlUrl}" target="_blank" download title="Tải văn bản về máy">
            📥 Tải về
          </a>
        </div>
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

// Xem trích đoạn văn bản trong modal
function showExcerptModal(title, excerpt) {
  document.getElementById('modalDocTitle').textContent = title;
  document.getElementById('modalDocExcerpt').textContent = excerpt || 'Không có trích đoạn hiển thị.';
  document.getElementById('docModal').classList.add('open');
}

// Đóng modal khi bấm ra ngoài vùng đen
function handleModalOverlayClick(e, modalId) {
  if (e.target.id === modalId) {
    document.getElementById(modalId).classList.remove('open');
  }
}

// Mở modal danh mục tất cả tài liệu có sẵn từ server
async function openAllDocsModal() {
  const modal = document.getElementById('allDocsModal');
  const container = document.getElementById('allDocsListContainer');
  modal.classList.add('open');
  try {
    const res = await fetch(`${API_BASE_URL}/api/documents`);
    const data = await res.json();
    window._allDocumentsCache = data.documents || [];
    renderDocsList(window._allDocumentsCache);
  } catch (err) {
    container.innerHTML = '<div style="padding:20px; color:#ef4444;">Không thể tải danh sách tài liệu.</div>';
  }
}

function closeAllDocsModal() {
  document.getElementById('allDocsModal').classList.remove('open');
}

function renderDocsList(docs) {
  const container = document.getElementById('allDocsListContainer');
  if (!docs.length) {
    container.innerHTML = '<div style="padding:20px; text-align:center;">Không tìm thấy tài liệu phù hợp.</div>';
    return;
  }
  container.innerHTML = docs.map(d => `
    <div style="display:flex; justify-content:space-between; align-items:center; padding:10px; border-bottom:1px solid #f1f5f9;">
      <div>
        <div style="font-weight:600; font-size:13px;">${escapeHTML(d.name)}</div>
        <div style="font-size:11px; color:#64748b;">${d.type} • ${d.size_kb} KB</div>
      </div>
      <a class="btn-badge-download" href="${API_BASE_URL}${d.download_url}" target="_blank" download>Tải về</a>
    </div>
  `).join('');
}

function filterDocsList(keyword) {
  if (!window._allDocumentsCache) return;
  const kw = keyword.toLowerCase();
  const filtered = window._allDocumentsCache.filter(d => d.name.toLowerCase().includes(kw));
  renderDocsList(filtered);
}

function quickFilterTopic(topic) {
  switchView('chat');
  sendQuestion('Hướng dẫn tra cứu các thông tin học vụ quan trọng');
}
