/**
 * ajax_toggle.js — CO5: AJAX Attendance Toggle
 * Sends POST request to toggle attendance without page refresh.
 * Used in admin_dashboard.html
 */

async function toggleAttendance(pk, btn) {
  btn.classList.add('loading');
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

  try {
    const res = await fetch(`/dashboard/toggle/${pk}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken || document.querySelector('[name=csrfmiddlewaretoken]')?.value,
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.status === 'ok') {
      const icon = btn.querySelector('.attendance-icon');
      icon.textContent = data.attendance ? '✅' : '⬜';
      icon.style.animation = 'pop 0.3s ease';
      setTimeout(() => { icon.style.animation = ''; }, 300);
    }
  } catch (err) {
    console.error('Toggle failed:', err);
    alert('Failed to update attendance. Please check your connection.');
  }
  btn.classList.remove('loading');
}
