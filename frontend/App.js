// App.js - Updated for Python Flask backend
import React, { useState, useEffect } from 'react';
import { ShoppingCart, Search, User, Menu, X, Star, Filter, Package, CreditCard, Truck } from 'lucide-react';

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
      
      const response = await fetch(`${API_BASE_URL}/products?${params}`);
      const data = await response.json();
      
      if (response.ok) {
        setProducts(data.products);
      } else {
        throw new Error(data.error || 'Failed to fetch products');
      }
    } catch (error) {
      console.error('Error fetching products:', error);
      setError(error.message);
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
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-8">
            <h1 
              className="text-2xl font-bold text-indigo-600 cursor-pointer"
              onClick={() => setCurrentView('home')}
            >
              ShopScale
            </h1>
            <nav className="hidden md:flex space-x-6">
              <button onClick={() => setCurrentView('home')} className="text-gray-700 hover:text-indigo-600">Home</button>
              <button onClick={() => setCurrentView('products')} className="text-gray-700 hover:text-indigo-600">Products</button>
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center bg-gray-100 rounded-lg px-4 py-2">
              <Search className="w-5 h-5 text-gray-400 mr-2" />
              <input
                type="text"
                placeholder="Search products..."
                className="bg-transparent outline-none w-64"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <button 
              onClick={() => setCurrentView('cart')}
              className="relative p-2 hover:bg-gray-100 rounded-full"
            >
              <ShoppingCart className="w-6 h-6" />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </button>

            {user ? (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">Hi, {user.first_name}</span>
                <button 
                  onClick={handleLogout}
                  className="bg-gray-200 px-3 py-1 rounded text-sm hover:bg-gray-300"
                >
                  Logout
                </button>
              </div>
            ) : (
              <button 
                onClick={() => setShowAuthModal(true)}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
              >
                Login
              </button>
            )}

            <button 
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );

  // Product Card Component
  const ProductCard = ({ product }) => (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition cursor-pointer">
      <img 
        src={product.image} 
        alt={product.name}
        className="w-full h-48 object-cover"
        onClick={() => {
          setSelectedProduct(product);
          setCurrentView('product-detail');
        }}
      />
      <div className="p-4">
        <h4 className="font-semibold text-lg mb-2 truncate">{product.name}</h4>
        <p className="text-gray-600 text-sm mb-2 truncate">{product.description}</p>
        <div className="flex items-center mb-2">
          <div className="flex">
            {[...Array(5)].map((_, i) => (
              <Star 
                key={i} 
                className={`w-4 h-4 ${i < product.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
              />
            ))}
          </div>
          <span className="text-sm text-gray-500 ml-2">({product.reviews})</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-2xl font-bold text-indigo-600">₹{product.price.toLocaleString()}</span>
          <button 
            onClick={() => addToCart(product)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );

  // Products View
  const ProductsView = () => (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Filters Sidebar */}
        <div className="md:w-64 flex-shrink-0">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-semibold text-lg mb-4 flex items-center">
              <Filter className="w-5 h-5 mr-2" />
              Filters
            </h3>
            <div className="space-y-2">
              {categories.map(category => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition ${
                    selectedCategory === category 
                      ? 'bg-indigo-600 text-white' 
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Products Grid */}
        <div className="flex-1">
          <div className="mb-4 flex justify-between items-center">
            <h2 className="text-2xl font-bold">All Products</h2>
            <span className="text-gray-600">{filteredProducts.length} products</span>
          </div>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading products...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h2 className="text-3xl font-bold mb-8">Shopping Cart</h2>
      {cart.length === 0 ? (
        <div className="text-center py-16">
          <ShoppingCart className="w-24 h-24 mx-auto text-gray-300 mb-4" />
          <p className="text-xl text-gray-600 mb-4">Your cart is empty</p>
          <button 
            onClick={() => setCurrentView('products')}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700"
          >
            Continue Shopping
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-4">
            {cart.map(item => (
              <div key={item.cart_item_id} className="bg-white rounded-lg shadow-md p-4 flex gap-4">
                <img src={item.image} alt={item.name} className="w-24 h-24 object-cover rounded" />
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{item.name}</h3>
                  <p className="text-gray-600">₹{item.price.toLocaleString()}</p>
                  <div className="flex items-center mt-2">
                    <button 
                      onClick={() => updateCartQuantity(item.cart_item_id, item.quantity - 1)}
                      className="bg-gray-200 px-3 py-1 rounded-l"
                    >
                      -
                    </button>
                    <span className="bg-gray-100 px-4 py-1">{item.quantity}</span>
                    <button 
                      onClick={() => updateCartQuantity(item.cart_item_id, item.quantity + 1)}
                      className="bg-gray-200 px-3 py-1 rounded-r"
                    >
                      +
                    </button>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">₹{(item.price * item.quantity).toLocaleString()}</p>
                  <button 
                    onClick={() => removeFromCart(item.cart_item_id)}
                    className="text-red-500 text-sm mt-2 hover:text-red-700"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
              <h3 className="text-xl font-bold mb-4">Order Summary</h3>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span>₹{cartTotal.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Shipping</span>
                  <span>₹500</span>
                </div>
                <div className="border-t pt-2 flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span>₹{(cartTotal + 500).toLocaleString()}</span>
                </div>
              </div>
              <button 
                onClick={() => setShowCheckout(true)}
                className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700"
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h3 className="text-2xl font-bold mb-4">
          {authMode === 'login' ? 'Login' : 'Register'}
        </h3>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
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
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">First Name</label>
                <input 
                  type="text" 
                  name="first_name" 
                  className="w-full border rounded-lg px-3 py-2" 
                  required 
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Last Name</label>
                <input 
                  type="text" 
                  name="last_name" 
                  className="w-full border rounded-lg px-3 py-2" 
                  required 
                />
              </div>
            </>
          )}
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Email</label>
            <input 
              type="email" 
              name="email" 
              className="w-full border rounded-lg px-3 py-2" 
              required 
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium mb-1">Password</label>
            <input 
              type="password" 
              name="password" 
              className="w-full border rounded-lg px-3 py-2" 
              required 
            />
          </div>
          
          <button 
            type="submit"
            className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 mb-4"
          >
            {authMode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>
        
        <button 
          onClick={() => {
            setAuthMode(authMode === 'login' ? 'register' : 'login');
            setError(null);
          }}
          className="w-full text-indigo-600 hover:text-indigo-700"
        >
          {authMode === 'login' ? 'Need an account? Register' : 'Have an account? Login'}
        </button>
        
        <button 
          onClick={() => setShowAuthModal(false)}
          className="w-full text-gray-600 hover:text-gray-700 mt-2"
        >
          Cancel
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      {currentView === 'home' && (
        <div>
          {/* Hero Section */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-5xl font-bold mb-4">Welcome to ShopScale</h2>
              <p className="text-xl mb-8">Discover amazing products at unbeatable prices</p>
              <button 
                onClick={() => setCurrentView('products')}
                className="bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
              >
                Shop Now
              </button>
            </div>
          </div>

          {/* Featured Products */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <h3 className="text-3xl font-bold mb-8">Featured Products</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {products.filter(p => p.featured).slice(0, 4).map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        </div>
      )}
      
      {currentView === 'products' && <ProductsView />}
      {currentView === 'cart' && <CartView />}
      
      {showAuthModal && <AuthModal />}
    </div>
  );
};

export default EcommercePlatform;