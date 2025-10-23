function renderDataChart() {
  const ctx = document.getElementById('dataChart');
  if (!ctx) return;
  
  // Destroy existing chart if it exists
  if (window.dataChartInstance) {
    window.dataChartInstance.destroy();
  }
  
  window.dataChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta'],
      datasets: [{
        label: 'Data Values',
        data: [4567, 3421, 5892, 2156, 7234, 4123],
        backgroundColor: [
          'rgba(29,233,182,0.7)',
          'rgba(0,229,255,0.7)',
          'rgba(233,29,182,0.7)',
          'rgba(255,229,0,0.7)',
          'rgba(29,233,182,0.7)',
          'rgba(0,229,255,0.7)'
        ],
        borderColor: [
          'rgba(29,233,182,1)',
          'rgba(0,229,255,1)',
          'rgba(233,29,182,1)',
          'rgba(255,229,0,1)',
          'rgba(29,233,182,1)',
          'rgba(0,229,255,1)'
        ],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: { 
            color: '#eaf6ff', 
            font: { weight: 'bold' } 
          }
        },
        title: {
          display: true,
          text: 'Data Overview',
          color: '#1de9b6',
          font: { size: 18 }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { 
            color: '#eaf6ff',
            font: { weight: 'bold' }
          },
          grid: { 
            color: 'rgba(29,233,182,0.2)',
            drawBorder: false
          }
        },
        x: {
          ticks: { 
            color: '#eaf6ff',
            font: { weight: 'bold' }
          },
          grid: { 
            color: 'rgba(29,233,182,0.2)',
            drawBorder: false
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    }
  });
}