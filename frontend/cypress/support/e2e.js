// Cypress support file - seed demo data and custom commands

// Capture console errors and uncaught exceptions from the AUT (application under test)
Cypress.on('window:before:load', (win) => {
  try {
    // store original
    win.__originalConsoleError = win.console.error;
    win.__consoleErrors = [];
    win.console.error = function (...args) {
      win.__consoleErrors.push({ args, ts: Date.now() });
      if (win.__originalConsoleError) {
        win.__originalConsoleError.apply(win.console, args);
      }
    };

    // capture uncaught exceptions
    win.__uncaughtErrors = [];
    const origOnError = win.onerror;
    win.onerror = function (msg, url, line, col, error) {
      win.__uncaughtErrors.push({ msg, url, line, col, error, ts: Date.now() });
      if (origOnError) origOnError.apply(this, arguments);
    };
  } catch (e) {
    // ignore
  }
});

Cypress.Commands.add('seedDemoData', () => {
  const users = [
    {
      id: 'user_demo_01',
      email: 'demo01',
      password: 'demo01',
      name: '테스트 사용자 01',
      role: 'user',
      createdAt: new Date().toISOString()
    },
    {
      id: 'admin_01',
      email: 'admin01',
      password: 'admin01',
      name: '관리자 01',
      role: 'admin',
      createdAt: new Date().toISOString()
    }
  ];

  window.localStorage.setItem('users', JSON.stringify(users));
  window.localStorage.setItem('test_accounts_initialized', 'true');
  window.localStorage.setItem('admin_accounts_initialized', 'true');

  // Clear or initialize other storages used in tests
  window.localStorage.setItem('orders', JSON.stringify([]));
  window.localStorage.setItem('recommendation_feedback', JSON.stringify([]));

  // Ensure guest id exists
  if (!window.localStorage.getItem('guest_user_id')) {
    const guestId = `guest_${Date.now()}_${Math.random().toString(36).slice(2,8)}`;
    window.localStorage.setItem('guest_user_id', guestId);
  }

  // cart and favorites per user
  window.localStorage.setItem('cart_user_demo_01', JSON.stringify([]));
  window.localStorage.setItem('favorites_user_demo_01', JSON.stringify([]));
});

// Optional: automatically seed before each test if desired
// beforeEach(() => {
//   cy.window().then((win) => {
//     cy.seedDemoData();
//   });
//});

