// Firebase Auth helper for the UI layer
(function () {
    window.authState = {
        isAuthenticated: false,
        user: null,
    };

    function initFirebase() {
        if (!window.firebase || !window.FIREBASE_CONFIG) {
            console.warn("Firebase not loaded or config missing");
            return null;
        }

        try {
            if (!firebase.apps.length) {
                firebase.initializeApp(window.FIREBASE_CONFIG);
            }
            return firebase.auth();
        } catch (err) {
            console.error('Firebase init error', err);
            return null;
        }
    }

    function handleAuthState(auth) {
        auth.onAuthStateChanged((user) => {
            window.authState.isAuthenticated = !!user;
            window.authState.user = user
                ? {
                      uid: user.uid,
                      email: user.email,
                      displayName: user.displayName,
                  }
                : null;

            const authBtn = document.getElementById('auth-btn');
            const userInfo = document.getElementById('user-info');
            const protectedEls = document.querySelectorAll('[data-protected]');
            const loginLink = document.getElementById('login-link');

            if (user) {
                if (authBtn) authBtn.textContent = 'Sign out';
                if (userInfo) userInfo.textContent = user.email || user.uid;
                protectedEls.forEach(e => e.style.display = 'block');
                if (loginLink) loginLink.style.display = 'none';

                // If on login page, redirect to home
                if (location.pathname === '/login') {
                    console.log('Auth successful, redirecting to home');
                    setTimeout(() => {
                        window.location.replace('/');
                    }, 500);
                }
            } else {
                if (authBtn) authBtn.textContent = 'Sign in';
                if (userInfo) userInfo.textContent = '';
                protectedEls.forEach(e => e.style.display = 'none');
                if (loginLink) loginLink.style.display = 'block';

                // If not on login page and not mounted (initial load), redirect to login
                if (location.pathname !== '/login' && !window.__initialLoadDone) {
                    console.log('User not authenticated, redirecting to login');
                    window.__initialLoadDone = true;
                    window.location.replace('/login');
                }
                window.__initialLoadDone = true;
            }
        });
    }

    window.toggleAuth = async function () {
        if (!window.firebase) return;

        const auth = firebase.auth();

        if (auth.currentUser) {
            try {
                await auth.signOut();
            } catch (err) {
                console.error('Sign out error', err);
            }
            return;
        }

        const provider = new firebase.auth.GoogleAuthProvider();

        try {
            await auth.signInWithPopup(provider);
        } catch (err) {
            console.error('Sign in error', err);

            // Handle popup blocked error
            if (err.code === 'auth/popup-blocked') {
                alert('Popup blocked. Trying redirect...');
                await auth.signInWithRedirect(provider);
            }
        }
    };

    window.getIdToken = async function () {
        if (!window.firebase) return null;
        const user = firebase.auth().currentUser;
        return user ? await user.getIdToken() : null;
    };

    function setupAuthUI() {
        const auth = initFirebase();
        if (!auth) return;

        handleAuthState(auth);

        const authBtn = document.getElementById('auth-btn');
        if (authBtn) {
            authBtn.onclick = window.toggleAuth;
        }
    }

    // Wait until everything is ready
    window.addEventListener('load', setupAuthUI);
})();