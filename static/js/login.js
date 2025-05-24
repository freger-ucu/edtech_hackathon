document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (password !== confirmPassword) {
            alert('Паролі не співпадають!');
            return;
        }
        
        if (username && email && password) {
            alert('Акаунт створено успішно!');
            console.log({
                username: username,
                email: email,
                password: password
            });
        } else {
            alert('Заповніть всі поля!');
        }
    });
    
    const loginLink = document.querySelector('.login-link');
    loginLink.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Перехід до сторінки входу');
    });
});