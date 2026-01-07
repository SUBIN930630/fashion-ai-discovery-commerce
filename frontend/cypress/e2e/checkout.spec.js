describe('Checkout flow', () => {
  it('logs in, adds a product to cart, and completes checkout', () => {
    cy.visit('/', {
      onBeforeLoad(win) {
        const users = [
          {
            id: 'user_demo_01',
            email: 'demo01',
            password: 'demo01',
            name: '테스트 사용자 01',
            role: 'user',
            createdAt: new Date().toISOString()
          }
        ];
        win.localStorage.setItem('users', JSON.stringify(users));
        win.localStorage.setItem('test_accounts_initialized', 'true');
        win.localStorage.setItem('admin_accounts_initialized', 'true');
        win.localStorage.setItem('orders', JSON.stringify([]));
        if (!win.localStorage.getItem('guest_user_id')) {
          win.localStorage.setItem('guest_user_id', `guest_${Date.now()}_${Math.random().toString(36).slice(2,8)}`);
        }
      }
    });

    // Remove webpack dev client overlay if it exists (can block clicks in Cypress).
    // Poll and remove repeatedly until it is gone, since it may be injected after load.
    cy.document().then((doc) => {
      return new Cypress.Promise((resolve) => {
        const interval = setInterval(() => {
          const overlay = doc.getElementById('webpack-dev-server-client-overlay');
          if (!overlay) {
            clearInterval(interval);
            resolve();
          } else if (overlay.parentNode) {
            overlay.parentNode.removeChild(overlay);
          }
        }, 200);
      });
    });

    // After loading, fail early if any console errors / uncaught exceptions occurred
    cy.window().then((win) => {
      const consoleErrors = win.__consoleErrors || [];
      const uncaught = win.__uncaughtErrors || [];
      if (consoleErrors.length || uncaught.length) {
        // Print to Cypress log for debugging then fail test
        // eslint-disable-next-line no-console
        console.error('Detected console errors:', consoleErrors);
        // eslint-disable-next-line no-console
        console.error('Detected uncaught errors:', uncaught);
        throw new Error(`Console/uncaught errors detected: ${consoleErrors.length} console errors, ${uncaught.length} uncaught errors`);
      }
    });

    // Ensure the webpack overlay is not present (flaky overlay can block interactions)
    cy.get('iframe#webpack-dev-server-client-overlay').should('not.exist');

    // Open login modal (force click in case overlay covers it)
    cy.contains('로그인').click({ force: true });

    // Fill login form with demo account
    cy.get('#email').type('demo01');
    cy.get('#password').type('demo01');
    cy.get('.auth-submit-button').click();

    // Wait for login to propagate
    cy.contains('마이페이지', { timeout: 5000 }).should('exist');

    // Add first product to cart
    cy.get('.product-card').first().within(() => {
      cy.get('.product-cart-button').click({ force: true });
    });

    // Open cart and go to checkout
    cy.get('.header-button.cart-button').click({ force: true });
    cy.get('.cart-checkout-button').click();

    // On checkout page
    cy.url().should('include', '/checkout');
    cy.get('.checkout-order-button').click();

    // On order complete page
    cy.url().should('include', '/order-complete');
    cy.contains('주문이 완료되었습니다!').should('exist');
  });
});
