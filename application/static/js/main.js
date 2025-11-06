// Initialize page with default home background
document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;
  body.classList.add('body-home');
  
  // Add content transition class to main content
  const mainContent = document.getElementById('main-content');
  if (mainContent) {
    mainContent.classList.add('content-transition', 'loaded');
  }
});

function loadContent(url) {
  const mainContent = document.getElementById('main-content');
  
  // Add loading state
  mainContent.classList.add('loading');
  mainContent.classList.remove('loaded');
  
  fetch(url)
    .then(response => response.text())
    .then(html => {
      // Update content
      mainContent.innerHTML = html;
      
      // Remove loading state and add loaded state with smooth fade-in
      mainContent.classList.remove('loading');
      setTimeout(() => {
        mainContent.classList.add('loaded', 'content-fade-in');
      }, 50);

      // Handle special content loading
      if (url === '/data') {
        loadDataChartScript();
      } else if (url === '/profile') {
        // Profile page has inline chart script, no additional loading needed
      }
    })
    .catch(error => {
      console.error('Error loading content:', error);
      mainContent.classList.remove('loading');
      mainContent.innerHTML = '<div class="text-center text-danger">Error loading content</div>';
    });
}

function loadDataChartScript() {
  // Remove previous data_chart.js if exists
  const oldScript = document.getElementById('datachart-script');
  if (oldScript) {
    oldScript.remove();
  }
  // Add new data_chart.js
  const script = document.createElement('script');
  script.src = '/static/js/data_chart.js';
  script.id = 'datachart-script';
  script.onload = () => {
    if (typeof renderDataChart === 'function') {
      renderDataChart();
    }
  };
  document.body.appendChild(script);
}

// Navigation event handlers with background changes
function handleNavigation(linkId, url, bodyClass) {
  const link = document.getElementById(linkId);
  if (link) {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Update active nav state
      document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      
  // Update body background
  const body = document.body;
  body.className = '';
  body.classList.add(bodyClass);
  console.log('Body class set to:', body.className); // DEBUG: Remove after testing
      
      // Load content
      loadContent(url);
    });
  }
}

// Set up all navigation handlers
handleNavigation('nav-data', '/data', 'body-data');
handleNavigation('nav-dashboard', '/dashboard', 'body-dashboard');
handleNavigation('nav-profile', '/profile', 'body-profile');
handleNavigation('nav-settings', '/settings', 'body-settings');

// Special handling for home button to avoid duplication
document.getElementById('nav-home').addEventListener('click', function(e) {
  e.preventDefault();

  // Update active nav state
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  this.classList.add('active');

  // Update body background
  const body = document.body;
  body.className = '';
  body.classList.add('body-home');

  // Load home content via AJAX so it matches initial page load
  loadContent('/');
});