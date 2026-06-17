/* ==========================================================================
   SkripsiEngineer Main Client JS - Academic Theme
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Landing Page AJAX Form Booking
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const field = document.getElementById('fieldSelect').value;
            const package = document.getElementById('packageSelect').value;
            const description = document.getElementById('descriptionInput').value;
            const preferredEl = document.getElementById('preferredDate');
            const preferred_date = preferredEl ? preferredEl.value : '';

            fetch('/api/requests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ field, package, description, preferred_date })
            })
            .then(res => {
                if (res.status === 401) {
                    alert('Anda harus masuk/login terlebih dahulu untuk mengajukan kelas.');
                    window.location.href = '/login';
                    return null;
                }
                return res.json();
            })
            .then(data => {
                if (data && data.status === 'success') {
                    alert('Pengajuan berhasil! Silakan cek dashboard Anda.');
                    window.location.href = '/dashboard';
                } else if (data) {
                    alert('Gagal mengirimkan pengajuan: ' + data.message);
                }
            })
            .catch(err => {
                console.error(err);
                alert('Terjadi kesalahan pengiriman.');
            });
        });
    }
});
