import React, { useState, useEffect } from 'react';
import { Package, Eye, Star, MessageSquare, Download } from 'lucide-react';

const OrderHistory = ({ user, authToken, API_BASE_URL }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      console.log('📦 Fetching orders from:', `${API_BASE_URL}/orders`);
      
      const response = await fetch(`${API_BASE_URL}/orders`, {
        headers: { 
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Orders fetched:', data.orders?.length || 0, 'orders');
        setOrders(data.orders || []);
      } else {
        const errorData = await response.json();
        console.error('❌ Failed to fetch orders:', errorData);
        alert('Error fetching orders: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('🔴 Network error fetching orders:', error);
      if (error.message.includes('Failed to fetch')) {
        alert('🔴 Connection Error: Cannot reach backend server');
      } else {
        alert('Error: ' + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (orderId) => {
    try {
      console.log('📋 Fetching order details for order:', orderId);
      
      const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
        headers: { 
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Order details fetched:', data);
        setSelectedOrder(data);
        setShowDetails(true);
      } else {
        const errorData = await response.json();
        console.error('❌ Failed to fetch order details:', errorData);
        alert('Error: ' + (errorData.error || 'Could not fetch order details'));
      }
    } catch (error) {
      console.error('🔴 Network error fetching order details:', error);
      if (error.message.includes('Failed to fetch')) {
        alert('🔴 Connection Error: Cannot reach backend server');
      } else {
        alert('Error: ' + error.message);
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#FFA500',
      confirmed: '#4169E1',
      processing: '#1E90FF',
      shipped: '#228B22',
      delivered: '#32CD32',
      cancelled: '#DC143C',
      returned: '#8B0000'
    };
    return colors[status] || '#000';
  };

  if (loading) {
    return <div className="loading">Loading your orders...</div>;
  }

  if (orders.length === 0) {
    return (
      <div className="empty-state">
        <Package size={48} />
        <h3>No Orders Yet</h3>
        <p>Start shopping to see your orders here</p>
      </div>
    );
  }

  return (
    <div className="order-history-container">
      <h2>Order History</h2>

      {showDetails && selectedOrder ? (
        <div className="order-details-modal">
          <button className="close-btn" onClick={() => setShowDetails(false)}>×</button>
          
          <div className="order-details">
            <h3>Order #{selectedOrder.order.order_id}</h3>
            
            <div className="details-grid">
              <div className="detail-section">
                <h4>Shipping Address</h4>
                <p>{selectedOrder.order.ship_street}</p>
                <p>{selectedOrder.order.ship_city}, {selectedOrder.order.ship_state}</p>
                <p>{selectedOrder.order.ship_postal}</p>
              </div>

              <div className="detail-section">
                <h4>Order Status</h4>
                <div
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(selectedOrder.order.order_status) }}
                >
                  {selectedOrder.order.order_status.toUpperCase()}
                </div>
              </div>

              <div className="detail-section">
                <h4>Payment Method</h4>
                <p>{selectedOrder.payment?.payment_method?.replace('_', ' ').toUpperCase()}</p>
              </div>
            </div>

            <div className="order-items-list">
              <h4>Items</h4>
              {selectedOrder.items.map((item) => (
                <div key={item.order_item_id} className="order-item-detail">
                  <img src={item.image} alt={item.product_name} />
                  <div>
                    <p className="item-name">{item.product_name}</p>
                    <p className="item-sku">SKU: {item.sku}</p>
                    <p>Qty: {item.quantity} × ₹{parseFloat(item.unit_price).toLocaleString()}</p>
                  </div>
                  <p className="item-total">₹{parseFloat(item.total_price).toLocaleString()}</p>
                </div>
              ))}
            </div>

            <div className="order-totals">
              <div className="total-row">
                <span>Subtotal:</span>
                <span>₹{(parseFloat(selectedOrder.order.total_amount) - parseFloat(selectedOrder.order.shipping_amount) - parseFloat(selectedOrder.order.tax_amount)).toLocaleString()}</span>
              </div>
              <div className="total-row">
                <span>Shipping:</span>
                <span>₹{parseFloat(selectedOrder.order.shipping_amount).toLocaleString()}</span>
              </div>
              <div className="total-row">
                <span>Tax:</span>
                <span>₹{parseFloat(selectedOrder.order.tax_amount).toLocaleString()}</span>
              </div>
              <div className="total-row total-amount">
                <span>Total:</span>
                <span>₹{parseFloat(selectedOrder.order.total_amount).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="orders-list">
          {orders.map((order) => (
            <div key={order.order_id} className="order-card">
              <div className="order-header">
                <div>
                  <p className="order-id">Order #{order.order_id}</p>
                  <p className="order-date">
                    {new Date(order.order_date).toLocaleDateString('en-IN', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}
                  </p>
                </div>
                <div
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(order.order_status) }}
                >
                  {order.order_status.toUpperCase()}
                </div>
              </div>

              <div className="order-body">
                <p className="order-total">
                  <strong>₹{parseFloat(order.total_amount).toLocaleString()}</strong>
                </p>
                <p className="order-items">Items: {order.order_id}</p>
              </div>

              <div className="order-footer">
                <button
                  className="btn btn-small btn-primary"
                  onClick={() => handleViewDetails(order.order_id)}
                >
                  <Eye size={16} /> View Details
                </button>
                {order.order_status === 'delivered' && (
                  <button className="btn btn-small btn-secondary">
                    <Star size={16} /> Write Review
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrderHistory;
