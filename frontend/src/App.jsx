import React, { useState, useEffect } from 'react';
import { ShoppingCart, Search, User, Menu, X, Star, Filter, Package, CreditCard, Truck, LogOut } from 'lucide-react';
import AdminLogin from './AdminLogin';
import AdminPanel from './AdminPanel';
import Checkout from './Checkout';
import OrderHistory from './OrderHistory';
import AddressManager from './AddressManager';
import ReviewSystem from './ReviewSystem';
import './App.css';
import './Ecommerce.css';

const EcommercePlatform = () => {
  const API_BASE_URL = 'http://localhost:5000/api';
  
  const [currentView, setCurrentView] = useState('home');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [cart, setCart] = useState([]);
  const [user, setUser] = useState(null);
  const [authToken, setAuthToken] = useState(localStorage.getItem('token') || null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [products, setProducts] = useState([]);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [adminUser, setAdminUser] = useState(null);
  const [showOrderHistory, setShowOrderHistory] = useState(false);
  const [showAddressManager, setShowAddressManager] = useState(false);

  const categories = ['all', 'Electronics', 'Clothing', 'Books', 'Home & Kitchen', 'Sports'];

  // Fetch products from API
  useEffect(() => {
    fetchProducts();
  }, [searchQuery, selectedCategory]);

  // Fetch user data if token exists
  useEffect(() => {
    if (authToken) {
      fetchCart();
    }
  }, [authToken]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (selectedCategory !== 'all') params.append('category', selectedCategory);
      
      console.log('🛍️ Fetching products from:', `${API_BASE_URL}/products?${params}`);
      
      const response = await fetch(`${API_BASE_URL}/products?${params}`);
      const data = await response.json();
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        setProducts(data.products);
        console.log('✅ Products fetched:', data.products?.length || 0);
      } else {
        throw new Error(data.error || 'Failed to fetch products');
      }
    } catch (error) {
      console.error('🔴 Error fetching products:', error);
      if (error.message.includes('Failed to fetch')) {
        setError('🔴 Connection Error: Cannot reach backend server');
      } else {
        setError(error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchCart = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/cart`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (response.ok) {
        const cartData = await response.json();
        setCart(cartData.items || []);
      }
    } catch (error) {
      console.error('Error fetching cart:', error);
    }
  };

  const addToCart = async (product) => {
    if (!authToken) {
      setShowAuthModal(true);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/cart/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          product_id: product.id,
          quantity: 1
        })
      });

      if (response.ok) {
        fetchCart(); // Refresh cart
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to add to cart');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      setError(error.message);
    }
  };

  const updateCartQuantity = async (itemId, newQuantity) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cart/items/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ quantity: newQuantity })
      });

      if (response.ok) {
        fetchCart(); // Refresh cart
      }
    } catch (error) {
      console.error('Error updating cart:', error);
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cart/items/${itemId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        fetchCart(); // Refresh cart
      }
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  };

  const handleLogin = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok) {
        setAuthToken(data.token);
        localStorage.setItem('token', data.token);
        setUser(data.customer);
        setShowAuthModal(false);
        setError(null);
        fetchCart(); // Load user's cart after login
      } else {
        throw new Error(data.error || 'Login failed');
      }
    } catch (error) {
      setError(error.message);
    }
  };

  const handleRegister = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      const data = await response.json();

      if (response.ok) {
        setAuthToken(data.token);
        localStorage.setItem('token', data.token);
        setUser(data.customer);
        setShowAuthModal(false);
        setError(null);
      } else {
        throw new Error(data.error || 'Registration failed');
      }
    } catch (error) {
      setError(error.message);
    }
  };

  const handleLogout = () => {
    setAuthToken(null);
    setUser(null);
    setCart([]);
    localStorage.removeItem('token');
  };

  // Filter products locally for immediate response
  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  // Header Component
  const Header = () => (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="header-left">
            <h1 
              className="logo"
              onClick={() => setCurrentView('home')}
            >
              ShopScale
            </h1>
            <nav className="nav">
              <button onClick={() => setCurrentView('home')} className="nav-link">Home</button>
              <button onClick={() => setCurrentView('products')} className="nav-link">Products</button>
            </nav>
          </div>

          <div className="header-right">
            <div className="search-container">
              <Search className="search-icon" />
              <input
                type="text"
                placeholder="Search products..."
                className="search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <button 
              onClick={() => setCurrentView('cart')}
              className="cart-button"
            >
              <ShoppingCart className="cart-icon" />
              {cartCount > 0 && (
                <span className="cart-badge">
                  {cartCount}
                </span>
              )}
            </button>

            {user ? (
              <div className="user-menu">
                <span className="user-greeting">Hi, {user.first_name}</span>
                <div className="user-actions">
                  <button 
                    onClick={() => setShowOrderHistory(true)}
                    className="btn btn-small"
                    title="View your orders"
                  >
                    <Package size={16} /> Orders
                  </button>
                  <button 
                    onClick={() => setShowAddressManager(true)}
                    className="btn btn-small"
                    title="Manage addresses"
                  >
                    📍 Addresses
                  </button>
                  {user.is_admin && (
                    <button 
                      onClick={() => setShowAdminLogin(true)}
                      className="admin-access-btn"
                    >
                      Admin Panel
                    </button>
                  )}
                  <button 
                    onClick={handleLogout}
                    className="btn btn-secondary"
                  >
                    <LogOut size={16} /> Logout
                  </button>
                </div>
              </div>
            ) : (
              <button 
                onClick={() => setShowAuthModal(true)}
                className="btn btn-primary"
              >
                <User size={18} /> Login
              </button>
            )}

            <button 
              className="mobile-menu-button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="menu-icon" /> : <Menu className="menu-icon" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );

  // Product Card Component
  const ProductCard = ({ product }) => (
    <div className="product-card">
      <img 
        src={product.image} 
        alt={product.name}
        className="product-image"
        onClick={() => {
          setSelectedProduct(product);
          setCurrentView('product-detail');
        }}
      />
      <div className="product-content">
        <h4 className="product-name">{product.name}</h4>
        <p className="product-description">{product.description}</p>
        <div className="product-rating">
          <div className="stars">
            {[...Array(5)].map((_, i) => (
              <Star 
                key={i} 
                className={`star-icon ${i < product.rating ? 'star-filled' : 'star-empty'}`}
              />
            ))}
          </div>
          <span className="review-count">({product.reviews})</span>
        </div>
        <div className="product-footer">
          <span className="product-price">₹{product.price.toLocaleString()}</span>
          <button 
            onClick={() => addToCart(product)}
            className="btn btn-primary add-to-cart-btn"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );

  // Products View
  const ProductsView = () => (
    <div className="container products-container">
      <div className="products-layout">
        {/* Filters Sidebar */}
        <div className="filters-sidebar">
          <div className="filters-card">
            <h3 className="filters-title">
              <Filter className="filter-icon" />
              Filters
            </h3>
            <div className="filters-list">
              {categories.map(category => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`filter-button ${selectedCategory === category ? 'filter-active' : ''}`}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Products Grid */}
        <div className="products-main">
          <div className="products-header">
            <h2 className="products-title">All Products</h2>
            <span className="products-count">{filteredProducts.length} products</span>
          </div>
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p className="loading-text">Loading products...</p>
            </div>
          ) : (
            <div className="products-grid">
              {filteredProducts.map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Cart View
  const CartView = () => (
    <div className="container cart-container">
      <h2 className="cart-title">Shopping Cart</h2>
      {cart.length === 0 ? (
        <div className="empty-cart">
          <ShoppingCart className="empty-cart-icon" />
          <p className="empty-cart-text">Your cart is empty</p>
          <button 
            onClick={() => setCurrentView('products')}
            className="btn btn-primary"
          >
            Continue Shopping
          </button>
        </div>
      ) : (
        <div className="cart-layout">
          <div className="cart-items">
            {cart.map(item => (
              <div key={item.cart_item_id} className="cart-item">
                <img src={item.image} alt={item.name} className="cart-item-image" />
                <div className="cart-item-details">
                  <h3 className="cart-item-name">{item.name}</h3>
                  <p className="cart-item-price">₹{item.price.toLocaleString()}</p>
                  <div className="quantity-controls">
                    <button 
                      onClick={() => updateCartQuantity(item.cart_item_id, item.quantity - 1)}
                      className="quantity-btn"
                    >
                      -
                    </button>
                    <span className="quantity-display">{item.quantity}</span>
                    <button 
                      onClick={() => updateCartQuantity(item.cart_item_id, item.quantity + 1)}
                      className="quantity-btn"
                    >
                      +
                    </button>
                  </div>
                </div>
                <div className="cart-item-total">
                  <p className="total-price">₹{(item.price * item.quantity).toLocaleString()}</p>
                  <button 
                    onClick={() => removeFromCart(item.cart_item_id)}
                    className="remove-btn"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="cart-summary">
            <div className="summary-card">
              <h3 className="summary-title">Order Summary</h3>
              <div className="summary-details">
                <div className="summary-row">
                  <span>Subtotal</span>
                  <span>₹{cartTotal.toLocaleString()}</span>
                </div>
                <div className="summary-row">
                  <span>Shipping</span>
                  <span>₹500</span>
                </div>
                <div className="summary-total">
                  <span>Total</span>
                  <span>₹{(cartTotal + 500).toLocaleString()}</span>
                </div>
              </div>
              <button 
                onClick={() => setShowCheckout(true)}
                className="btn btn-primary checkout-btn"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Authentication Modal
  const AuthModal = () => (
    <div className="modal-overlay">
      <div className="modal">
        <h3 className="modal-title">
          {authMode === 'login' ? 'Login' : 'Register'}
        </h3>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target);
          const data = Object.fromEntries(formData);
          
          if (authMode === 'login') {
            handleLogin(data.email, data.password);
          } else {
            handleRegister(data);
          }
        }}>
          {authMode === 'register' && (
            <>
              <div className="form-group">
                <label className="form-label">First Name</label>
                <input 
                  type="text" 
                  name="first_name" 
                  className="form-input" 
                  required 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Last Name</label>
                <input 
                  type="text" 
                  name="last_name" 
                  className="form-input" 
                  required 
                />
              </div>
            </>
          )}
          
          <div className="form-group">
            <label className="form-label">Email</label>
            <input 
              type="email" 
              name="email" 
              className="form-input" 
              required 
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Password</label>
            <input 
              type="password" 
              name="password" 
              className="form-input" 
              required 
            />
          </div>
          
          <button 
            type="submit"
            className="btn btn-primary modal-submit-btn"
          >
            {authMode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>
        
        <button 
          onClick={() => {
            setAuthMode(authMode === 'login' ? 'register' : 'login');
            setError(null);
          }}
          className="auth-switch-btn"
        >
          {authMode === 'login' ? 'Need an account? Register' : 'Have an account? Login'}
        </button>
        
        <button 
          onClick={() => setShowAuthModal(false)}
          className="modal-cancel-btn"
        >
          Cancel
        </button>
      </div>
    </div>
  );

  // Footer Component
  const Footer = () => (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h4 className="footer-title">About ShopScale</h4>
            <p className="footer-description">
              Your one-stop destination for quality products at unbeatable prices. 
              Shop with confidence and ease.
            </p>
          </div>
          <div className="footer-section">
            <h4 className="footer-title">Quick Links</h4>
            <ul className="footer-links">
              <li><button onClick={() => setCurrentView('home')} className="footer-link">Home</button></li>
              <li><button onClick={() => setCurrentView('products')} className="footer-link">Products</button></li>
              <li><button className="footer-link">About Us</button></li>
              <li><button className="footer-link">Contact</button></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="footer-title">Customer Service</h4>
            <ul className="footer-links">
              <li><button className="footer-link">FAQ</button></li>
              <li><button className="footer-link">Shipping Info</button></li>
              <li><button className="footer-link">Returns</button></li>
              <li><button className="footer-link">Privacy Policy</button></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4 className="footer-title">Contact Us</h4>
            <p className="footer-contact">
              Email: support@shopscale.com<br/>
              Phone: +91 1234567890<br/>
              Address: New Delhi, India
            </p>
          </div>
        </div>
        <div className="footer-bottom">
          <p className="footer-copyright">
            &copy; 2024 ShopScale. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );

  // Home View
  const HomeView = () => (
    <div>
      {/* Hero Section */}
      <div className="hero-section">
        <div className="container text-center">
          <h2 className="hero-title">Welcome to ShopScale</h2>
          <p className="hero-subtitle">Discover amazing products at unbeatable prices</p>
          <button 
            onClick={() => setCurrentView('products')}
            className="btn btn-primary hero-btn"
          >
            Shop Now
          </button>
        </div>
      </div>

      {/* Featured Products */}
      <div className="container featured-section">
        <h3 className="section-title">Featured Products</h3>
        <div className="featured-grid">
          {products.filter(p => p.featured).slice(0, 4).map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="features-section">
        <div className="container">
          <div className="features-grid">
            <div className="feature-item text-center">
              <Truck className="feature-icon" />
              <h4 className="feature-title">Free Shipping</h4>
              <p className="feature-description">On orders over ₹1000</p>
            </div>
            <div className="feature-item text-center">
              <CreditCard className="feature-icon" />
              <h4 className="feature-title">Secure Payment</h4>
              <p className="feature-description">100% secure transactions</p>
            </div>
            <div className="feature-item text-center">
              <Package className="feature-icon" />
              <h4 className="feature-title">Easy Returns</h4>
              <p className="feature-description">30-day return policy</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Admin login handler
  const handleAdminLogin = (user) => {
    setAdminUser(user);
    setShowAdminLogin(false);
    setShowAdminPanel(true);
  };

  return (
    <div className="app">
      {showAdminLogin ? (
        <AdminLogin 
          onLoginSuccess={handleAdminLogin}
          onBackToStore={() => setShowAdminLogin(false)}
        />
      ) : showAdminPanel ? (
        <AdminPanel 
          onBackToStore={() => {
            setShowAdminPanel(false);
            setAdminUser(null);
          }}
          adminUser={adminUser}
        />
      ) : (
        <div>
          <Header />
          
          <main className="main-content">
            {currentView === 'home' && <HomeView />}
            {currentView === 'products' && <ProductsView />}
            {currentView === 'cart' && !showCheckout && <CartView />}
            {currentView === 'cart' && showCheckout && user && authToken && (
              <Checkout 
                cartItems={cart}
                cartTotal={cartTotal}
                user={user}
                authToken={authToken}
                API_BASE_URL={API_BASE_URL}
                onCheckoutComplete={(orderId) => {
                  setShowCheckout(false);
                  setCurrentView('home');
                  setCart([]);
                  alert(`Order #${orderId} placed successfully!`);
                }}
                onBack={() => setShowCheckout(false)}
              />
            )}
            {currentView === 'product-detail' && selectedProduct && (
              <div className="product-detail-view">
                <button 
                  onClick={() => setCurrentView('products')}
                  className="btn btn-secondary"
                  style={{ marginBottom: '1.5rem' }}
                >
                  ← Back to Products
                </button>
                <div className="product-detail-container">
                  <div className="product-detail-image">
                    <img src={selectedProduct.image} alt={selectedProduct.name} />
                  </div>
                  <div className="product-detail-info">
                    <h2>{selectedProduct.name}</h2>
                    <p className="detail-description">{selectedProduct.description}</p>
                    <p className="detail-price">₹{selectedProduct.price?.toLocaleString() || 'N/A'}</p>
                    <p className="detail-stock">
                      Stock: <strong>{selectedProduct.stock_quantity || 0} units</strong>
                    </p>
                    <button 
                      onClick={() => {
                        addToCart(selectedProduct);
                        alert('Added to cart!');
                      }}
                      className="btn btn-primary"
                      style={{ fontSize: '1.1rem', padding: '0.75rem 2rem' }}
                    >
                      Add to Cart
                    </button>
                  </div>
                </div>
                <ReviewSystem 
                  product={selectedProduct}
                  user={user}
                  authToken={authToken}
                  API_BASE_URL={API_BASE_URL}
                />
              </div>
            )}
          </main>

          {/* Modals */}
          {showAuthModal && <AuthModal />}
          {showOrderHistory && user && authToken && (
            <div className="modal-overlay" onClick={() => setShowOrderHistory(false)}>
              <div className="modal-lg-content" onClick={(e) => e.stopPropagation()}>
                <button 
                  className="close-btn" 
                  onClick={() => setShowOrderHistory(false)}
                >
                  ×
                </button>
                <OrderHistory 
                  user={user}
                  authToken={authToken}
                  API_BASE_URL={API_BASE_URL}
                />
              </div>
            </div>
          )}
          
          <AddressManager
            isOpen={showAddressManager}
            onClose={() => setShowAddressManager(false)}
            onSelectAddress={(address) => {
              setShowAddressManager(false);
              if (currentView === 'cart') {
                setShowCheckout(true);
              }
            }}
            authToken={authToken}
            API_BASE_URL={API_BASE_URL}
          />

          <Footer />
        </div>
      )}
    </div>
  );
};

export default EcommercePlatform;