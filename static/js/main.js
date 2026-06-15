document.addEventListener("DOMContentLoaded", () => {
    updateNav();

    // Login Form
    const loginForm = document.getElementById('login-form');
    if(loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new URLSearchParams();
            formData.append('username', document.getElementById('login-username').value);
            formData.append('password', document.getElementById('login-password').value);
            
            try {
                const res = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });
                
                if(res.ok) {
                    const data = await res.json();
                    localStorage.setItem('access_token', data.access_token);
                    window.location.href = '/';
                } else {
                    alert('Login failed. Check credentials.');
                }
            } catch(e) {
                console.error(e);
            }
        });
    }

    // Register Form
    const regForm = document.getElementById('register-form');
    if(regForm) {
        regForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                username: document.getElementById('reg-username').value,
                email: document.getElementById('reg-email').value,
                password: document.getElementById('reg-password').value
            };
            
            try {
                const res = await fetch('/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if(res.ok) {
                    alert('Registration successful! Please login.');
                    document.getElementById('pills-login-tab').click();
                } else {
                    alert('Registration failed. Username/email might be taken.');
                }
            } catch(e) {
                console.error(e);
            }
        });
    }

    // Upload Form
    const uploadForm = document.getElementById('upload-form');
    if(uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = localStorage.getItem('access_token');
            if(!token) return alert('You must be logged in to upload.');

            const btn = document.getElementById('upload-btn');
            btn.disabled = true;
            btn.innerText = 'Uploading...';

            const formData = new FormData();
            formData.append('title', document.getElementById('video-title').value);
            formData.append('description', document.getElementById('video-desc').value);
            formData.append('tags', document.getElementById('video-tags').value);
            formData.append('video_file', document.getElementById('video-file').files[0]);
            const thumbInput = document.getElementById('thumbnail-file');
            if(thumbInput && thumbInput.files[0]) {
                formData.append('thumbnail_file', thumbInput.files[0]);
            }

            try {
                const res = await fetch('/videos/upload', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });
                
                if(res.ok) {
                    alert('Upload successful!');
                    window.location.href = '/';
                } else {
                    alert('Upload failed.');
                    btn.disabled = false;
                    btn.innerText = 'Upload Video';
                }
            } catch(e) {
                console.error(e);
                btn.disabled = false;
                btn.innerText = 'Upload Video';
            }
        });
    }

    // Search Form
    const searchForm = document.getElementById('search-form');
    if(searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const q = document.getElementById('search-input').value;
            window.location.href = '/?q=' + encodeURIComponent(q);
        });
    }
});

async function updateNav() {
    const navLinks = document.getElementById('nav-links');
    if(!navLinks) return;

    const token = localStorage.getItem('access_token');
    if(token) {
        try {
            const res = await fetch('/auth/me', { headers: { 'Authorization': `Bearer ${token}` } });
            if(res.ok) {
                const user = await res.json();
                navLinks.innerHTML = `
                    <li class="nav-item me-3 d-flex align-items-center">
                        <a class="btn btn-light rounded-pill px-4 fw-bold shadow-sm d-flex align-items-center text-dark" href="/upload">
                            <i class="bi bi-plus-circle-fill me-2 fs-5 text-danger"></i> Upload Video
                        </a>
                    </li>
                    <li class="nav-item dropdown d-flex align-items-center">
                        <a class="nav-link dropdown-toggle text-white fw-bold d-flex align-items-center" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="bi bi-person-circle fs-4 me-2 text-secondary"></i> ${user.username}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end dropdown-menu-dark shadow border-secondary mt-2" aria-labelledby="userDropdown">
                            <li><a class="dropdown-item py-2" href="/history"><i class="bi bi-clock-history me-2"></i> Watch History</a></li>
                            <li><a class="dropdown-item py-2" href="/liked"><i class="bi bi-hand-thumbs-up me-2"></i> Liked Videos</a></li>
                            <li><hr class="dropdown-divider border-secondary"></li>
                            <li><a class="dropdown-item text-danger fw-bold py-2" href="#" onclick="logout()"><i class="bi bi-box-arrow-right me-2"></i> Sign Out</a></li>
                        </ul>
                    </li>
                `;
            } else {
                localStorage.removeItem('access_token');
                renderLoginNav(navLinks);
            }
        } catch(e) {
            renderLoginNav(navLinks);
        }
    } else {
        renderLoginNav(navLinks);
    }
}

function renderLoginNav(navLinks) {
    navLinks.innerHTML = `
        <li class="nav-item d-flex align-items-center">
            <a class="btn btn-outline-primary rounded-pill px-4 fw-bold" href="/login">
                <i class="bi bi-person-circle me-2"></i> Sign In
            </a>
        </li>
    `;
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
}
