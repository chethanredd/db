// src/AdminPanel.jsx
import React, { useState, useEffect } from 'react';
import { 
    Package, 
    Users, 
    ShoppingCart, 
    DollarSign, 
    BarChart3, 
    Plus, 
    Edit, 
    Trash2,
    X,
    Save,
    Home
} from 'lucide-react';
import './AdminPanel.css';

const AdminPanel = ({ onBackToStore }) => {
    const API_BASE_URL = 'http://localhost:5000/api';
    const [currentSection, setCurrentSection] = useState('dashboard');
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showProductForm, setShowProductForm] = useState(false);
    const [editingProduct, setEditingProduct] = useState(null);
    const [dashboardStats, setDashboardStats] = useState(null);
    const [authToken] = useState(localStorage.getItem('token'));

    // Form state
    const [productForm, setProductForm] = useState({
        product_name: '',
        description: '',
        price: '',
        cost_price: '',
        stock_quantity: '',
        sku: '',
        brand: '',
        weight: '',
        dimensions: '',
        color: '',
        size: '',
        is_active: true,
        featured: false,
        image: '',
        categories: []
    });

    useEffect(() => {
        if (currentSection === 'products') {
            fetchProducts();
            fetchCategories();
        } else if (currentSection === 'dashboard') {
            fetchDashboardStats();
        }
    }, [currentSection]);

    const fetchProducts = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE_URL}/admin/products`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setProducts(data.products);
            } else {
                throw new Error('Failed to fetch products');
            }
        } catch (error) {
            console.error('Error fetching products:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/categories`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setCategories(data);
            }
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const fetchDashboardStats = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setDashboardStats(data);
            }
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
        }
    };

    const resetProductForm = () => {
        setProductForm({
            product_name: '',
            description: '',
            price: '',
            cost_price: '',
            stock_quantity: '',
            sku: '',
            brand: '',
            weight: '',
            dimensions: '',
            color: '',
            size: '',
            is_active: true,
            featured: false,
            image: '',
            categories: []
        });
        setEditingProduct(null);
    };

    const handleCreateProduct = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${API_BASE_URL}/admin/products`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(productForm)
            });

            if (response.ok) {
                setShowProductForm(false);
                resetProductForm();
                fetchProducts();
                setError(null);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to create product');
            }
        } catch (error) {
            console.error('Error creating product:', error);
            setError(error.message);
        }
    };

    const handleUpdateProduct = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${API_BASE_URL}/admin/products/${editingProduct.product_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(productForm)
            });

            if (response.ok) {
                setShowProductForm(false);
                resetProductForm();
                fetchProducts();
                setError(null);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update product');
            }
        } catch (error) {
            console.error('Error updating product:', error);
            setError(error.message);
        }
    };

    const handleDeleteProduct = async (productId) => {
        if (!window.confirm('Are you sure you want to delete this product?')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/admin/products/${productId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            if (response.ok) {
                fetchProducts();
                setError(null);
            } else {
                throw new Error('Failed to delete product');
            }
        } catch (error) {
            console.error('Error deleting product:', error);
            setError(error.message);
        }
    };

    const handleEditProduct = (product) => {
        setEditingProduct(product);
        setProductForm({
            product_name: product.product_name,
            description: product.description || '',
            price: product.price,
            cost_price: product.cost_price || '',
            stock_quantity: product.stock_quantity,
            sku: product.sku,
            brand: product.brand || '',
            weight: product.weight || '',
            dimensions: product.dimensions || '',
            color: product.color || '',
            size: product.size || '',
            is_active: product.is_active,
            featured: product.featured,
            image: product.image || '',
            categories: product.categories ? product.categories.split(',').map(cat => {
                const category = categories.find(c => c.category_name === cat.trim());
                return category ? category.category_id : null;
            }).filter(Boolean) : []
        });
        setShowProductForm(true);
    };

    const testDatabaseFunctions = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/test-db-functions`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                alert('Database functions tested successfully! Check console for details.');
                console.log('Database Functions Test Results:', data);
            } else {
                throw new Error('Failed to test database functions');
            }
        } catch (error) {
            console.error('Error testing database functions:', error);
            alert('Error testing database functions: ' + error.message);
        }
    };

    // Dashboard Component
    const Dashboard = () => {
        if (!dashboardStats) {
            return <div className="loading">Loading dashboard...</div>;
        }

        return (
            <div className="dashboard">
                <div className="dashboard-header">
                    <h2>Admin Dashboard</h2>
                    <button onClick={testDatabaseFunctions} className="btn btn-secondary">
                        Test Database Functions
                    </button>
                </div>
                
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon revenue">
                            <DollarSign />
                        </div>
                        <div className="stat-info">
                            <h3>₹{dashboardStats.sales?.total_revenue?.toLocaleString() || '0'}</h3>
                            <p>Total Revenue</p>
                        </div>
                    </div>
                    
                    <div className="stat-card">
                        <div className="stat-icon orders">
                            <ShoppingCart />
                        </div>
                        <div className="stat-info">
                            <h3>{dashboardStats.sales?.total_orders || '0'}</h3>
                            <p>Total Orders</p>
                        </div>
                    </div>
                    
                    <div className="stat-card">
                        <div className="stat-icon products">
                            <Package />
                        </div>
                        <div className="stat-info">
                            <h3>{dashboardStats.products?.total_products || '0'}</h3>
                            <p>Total Products</p>
                        </div>
                    </div>
                    
                    <div className="stat-card">
                        <div className="stat-icon customers">
                            <Users />
                        </div>
                        <div className="stat-info">
                            <h3>{dashboardStats.customers?.total_customers || '0'}</h3>
                            <p>Total Customers</p>
                        </div>
                    </div>
                </div>

                <div className="recent-orders">
                    <h3>Recent Orders</h3>
                    <div className="orders-list">
                        {dashboardStats.recent_orders?.map(order => (
                            <div key={order.order_id} className="order-item">
                                <div className="order-info">
                                    <strong>Order #{order.order_id}</strong>
                                    <span>{order.customer_name}</span>
                                </div>
                                <div className="order-details">
                                    <span>₹{order.total_amount?.toLocaleString()}</span>
                                    <span className={`status ${order.order_status}`}>
                                        {order.order_status}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    };

    // Products Management Component
    const ProductsManagement = () => (
        <div className="products-management">
            <div className="section-header">
                <h2>Products Management</h2>
                <button 
                    onClick={() => {
                        resetProductForm();
                        setShowProductForm(true);
                    }}
                    className="btn btn-primary"
                >
                    <Plus size={16} />
                    Add Product
                </button>
            </div>

            {loading ? (
                <div className="loading">Loading products...</div>
            ) : (
                <div className="products-table-container">
                    <table className="products-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>SKU</th>
                                <th>Price</th>
                                <th>Stock</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map(product => (
                                <tr key={product.product_id}>
                                    <td>{product.product_id}</td>
                                    <td>
                                        <div className="product-info">
                                            {product.image && (
                                                <img 
                                                    src={product.image} 
                                                    alt={product.product_name}
                                                    className="product-thumbnail"
                                                />
                                            )}
                                            <span>{product.product_name}</span>
                                        </div>
                                    </td>
                                    <td>{product.sku}</td>
                                    <td>₹{parseFloat(product.price).toLocaleString()}</td>
                                    <td>
                                        <span className={`stock ${product.stock_quantity > 0 ? 'in-stock' : 'out-of-stock'}`}>
                                            {product.stock_quantity}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`status ${product.is_active ? 'active' : 'inactive'}`}>
                                            {product.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="actions">
                                            <button 
                                                onClick={() => handleEditProduct(product)}
                                                className="btn-icon edit"
                                            >
                                                <Edit size={16} />
                                            </button>
                                            <button 
                                                onClick={() => handleDeleteProduct(product.product_id)}
                                                className="btn-icon delete"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );

    // Product Form Modal
    const ProductFormModal = () => (
        <div className="modal-overlay">
            <div className="modal product-form-modal">
                <div className="modal-header">
                    <h3>{editingProduct ? 'Edit Product' : 'Add New Product'}</h3>
                    <button 
                        onClick={() => {
                            setShowProductForm(false);
                            resetProductForm();
                        }}
                        className="btn-icon"
                    >
                        <X size={20} />
                    </button>
                </div>

                {error && (
                    <div className="error-message">{error}</div>
                )}

                <form onSubmit={editingProduct ? handleUpdateProduct : handleCreateProduct}>
                    <div className="form-grid">
                        <div className="form-group">
                            <label className="form-label">Product Name *</label>
                            <input
                                type="text"
                                className="form-input"
                                value={productForm.product_name}
                                onChange={(e) => setProductForm({...productForm, product_name: e.target.value})}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">SKU *</label>
                            <input
                                type="text"
                                className="form-input"
                                value={productForm.sku}
                                onChange={(e) => setProductForm({...productForm, sku: e.target.value})}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Price *</label>
                            <input
                                type="number"
                                step="0.01"
                                className="form-input"
                                value={productForm.price}
                                onChange={(e) => setProductForm({...productForm, price: e.target.value})}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Cost Price</label>
                            <input
                                type="number"
                                step="0.01"
                                className="form-input"
                                value={productForm.cost_price}
                                onChange={(e) => setProductForm({...productForm, cost_price: e.target.value})}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Stock Quantity *</label>
                            <input
                                type="number"
                                className="form-input"
                                value={productForm.stock_quantity}
                                onChange={(e) => setProductForm({...productForm, stock_quantity: e.target.value})}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Brand</label>
                            <input
                                type="text"
                                className="form-input"
                                value={productForm.brand}
                                onChange={(e) => setProductForm({...productForm, brand: e.target.value})}
                            />
                        </div>

                        <div className="form-group full-width">
                            <label className="form-label">Description</label>
                            <textarea
                                className="form-input"
                                rows="3"
                                value={productForm.description}
                                onChange={(e) => setProductForm({...productForm, description: e.target.value})}
                            />
                        </div>

                        <div className="form-group full-width">
                            <label className="form-label">Categories</label>
                            <div className="categories-checkboxes">
                                {categories.map(category => (
                                    <label key={category.category_id} className="checkbox-label">
                                        <input
                                            type="checkbox"
                                            checked={productForm.categories.includes(category.category_id)}
                                            onChange={(e) => {
                                                const updatedCategories = e.target.checked
                                                    ? [...productForm.categories, category.category_id]
                                                    : productForm.categories.filter(id => id !== category.category_id);
                                                setProductForm({...productForm, categories: updatedCategories});
                                            }}
                                        />
                                        {category.category_name}
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Image URL</label>
                            <input
                                type="url"
                                className="form-input"
                                value={productForm.image}
                                onChange={(e) => setProductForm({...productForm, image: e.target.value})}
                            />
                        </div>

                        <div className="form-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={productForm.is_active}
                                    onChange={(e) => setProductForm({...productForm, is_active: e.target.checked})}
                                />
                                Active
                            </label>
                        </div>

                        <div className="form-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={productForm.featured}
                                    onChange={(e) => setProductForm({...productForm, featured: e.target.checked})}
                                />
                                Featured
                            </label>
                        </div>
                    </div>

                    <div className="form-actions">
                        <button
                            type="button"
                            onClick={() => {
                                setShowProductForm(false);
                                resetProductForm();
                            }}
                            className="btn btn-secondary"
                        >
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-primary">
                            <Save size={16} />
                            {editingProduct ? 'Update Product' : 'Create Product'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );

    return (
        <div className="admin-panel">
            <div className="admin-sidebar">
                <div className="sidebar-header">
                    <h2>ShopScale Admin</h2>
                </div>
                <nav className="sidebar-nav">
                    <button 
                        onClick={() => setCurrentSection('dashboard')}
                        className={`nav-item ${currentSection === 'dashboard' ? 'active' : ''}`}
                    >
                        <BarChart3 size={20} />
                        Dashboard
                    </button>
                    <button 
                        onClick={() => setCurrentSection('products')}
                        className={`nav-item ${currentSection === 'products' ? 'active' : ''}`}
                    >
                        <Package size={20} />
                        Products
                    </button>
                    <button 
                        onClick={onBackToStore}
                        className="nav-item back-to-store"
                    >
                        <Home size={20} />
                        Back to Store
                    </button>
                </nav>
            </div>

            <div className="admin-content">
                {currentSection === 'dashboard' && <Dashboard />}
                {currentSection === 'products' && <ProductsManagement />}
            </div>

            {showProductForm && <ProductFormModal />}
        </div>
    );
};

export default AdminPanel;