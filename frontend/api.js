import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add a request interceptor to include the token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (userData) => api.post('/auth/register', userData),
};

export const productsAPI = {
  getProducts: (params) => api.get('/products', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
};

export const cartAPI = {
  getCart: () => api.get('/cart'),
  addToCart: (productId, quantity) => api.post('/cart/items', { product_id: productId, quantity }),
  updateCartItem: (itemId, quantity) => api.put(`/cart/items/${itemId}`, { quantity }),
  removeCartItem: (itemId) => api.delete(`/cart/items/${itemId}`),
};

export const ordersAPI = {
  getOrders: () => api.get('/orders'),
  createOrder: (orderData) => api.post('/orders', orderData),
  getOrder: (id) => api.get(`/orders/${id}`),
  cancelOrder: (id) => api.put(`/orders/${id}/cancel`),
};

export const customersAPI = {
  getProfile: () => api.get('/customers/profile'),
  updateProfile: (profileData) => api.put('/customers/profile', profileData),
  getAddresses: () => api.get('/customers/addresses'),
  addAddress: (addressData) => api.post('/customers/addresses', addressData),
};

export const reviewsAPI = {
  createReview: (reviewData) => api.post('/reviews', reviewData),
};

export default api;