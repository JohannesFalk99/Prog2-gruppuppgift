document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('annotationsSidebar');
  const content = document.getElementById('annotationsSidebarContent');
  const toggle = document.getElementById('toggleAnnotations');
  const closeBtn = document.getElementById('closeAnnotations');

  function openSidebar() {
    sidebar.classList.add('open');
    loadAnnotations();
  }
  function closeSidebar() { sidebar.classList.remove('open'); }

  toggle && toggle.addEventListener('click', openSidebar);
  closeBtn && closeBtn.addEventListener('click', closeSidebar);

  async function loadAnnotations() {
    content.innerHTML = '<div class="text-muted small">Loading annotations...</div>';
    try {
      // get current date/area from page inputs if they exist
      const dateInput = document.getElementById('fetchDate');
      const areaInput = document.getElementById('prisklass');
      const date = dateInput ? dateInput.value : '';
      const area = areaInput ? areaInput.value : '';
      if (!date) {
        content.innerHTML = '<div class="text-muted small">No date selected</div>';
        return;
      }
      const qs = `?date=${encodeURIComponent(date)}&prisklass=${encodeURIComponent(area)}`;
      const res = await fetch('/annotations' + qs);
      if (!res.ok) {
        content.innerHTML = '<div class="text-danger small">Failed to load annotations</div>';
        return;
      }
      const j = await res.json();
      const anns = j.annotations || [];
      if (!anns.length) {
        content.innerHTML = '<div class="text-muted small">No annotations for selected date/area.</div>';
        return;
      }
      // render list
      const list = document.createElement('div');
      list.className = 'list-group';
      anns.forEach(a => {
        const item = document.createElement('div');
        item.className = 'list-group-item';
        const title = document.createElement('div');
        title.className = 'fw-bold';
        title.textContent = `${a.author || 'anonymous'} ${a.hour ? '('+a.hour+')' : ''}`;
        const text = document.createElement('div');
        text.textContent = a.text || '';
        const meta = document.createElement('div');
        meta.className = 'small text-muted';
        meta.textContent = `${a.created_at || ''} • 👍 ${a.likes||0} 👎 ${a.dislikes||0}`;
        item.appendChild(title);
        item.appendChild(text);
        item.appendChild(meta);
        list.appendChild(item);
      });
      content.innerHTML = '';
      content.appendChild(list);
    } catch (e) {
      console.error('Annotations load failed', e);
      content.innerHTML = '<div class="text-danger small">Error loading annotations</div>';
    }
  }
});
