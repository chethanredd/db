import React, { useState, useEffect } from 'react';
import { ShoppingBag, MapPin, CreditCard, Package, Loader } from 'lucide-react';
import AddressManager from './AddressManager';

const Checkout = ({ cartItems, cartTotal, user, authToken, API_BASE_URL, onCheckoutComplete, onBack }) => {
  const [step, setStep] = useState(1);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [loading, setLoading] = useState(false);
  const [showAddressManager, setShowAddressManager] = useState(false);
  const [orderSummary, setOrderSummary] = useState({
    subtotal: cartTotal,
    shipping: cartTotal >= 1000 ? 0 : 100,
    tax: 0,
    total: 0
  });

  useEffect(() => {
    const tax = cartTotal * 0.18;
    const total = cartTotal + orderSummary.shipping + tax;
    setOrderSummary({
      subtotal: cartTotal,
      shipping: cartTotal >= 1000 ? 0 : 100,
      tax,
      total
    });
  }, [cartTotal]);

  const handleSelectAddress = (address) => {
    setSelectedAddress(address);
    setShowAddressManager(false);
    setStep(2);
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddress || !paymentMethod) {
      alert('❌ Please select an address and payment method');
      return;
    }

    setLoading(true);
    try {
      const submitURL = `${API_BASE_URL}/orders/create`;
      console.log('📤 Placing order to:', submitURL);
      console.log('📋 Order data:', {
        shipping_address_id: selectedAddress.address_id,
        billing_address_id: selectedAddress.address_id,
        payment_method: paymentMethod
      });
      
      const response = await fetch(submitURL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          shipping_address_id: selectedAddress.address_id,
          billing_address_id: selectedAddress.address_id,
          payment_method: paymentMethod
        })
      });

      console.log('📥 Response status:', response.status, response.statusText);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Order created successfully:', data);
        setStep(3);
        setTimeout(() => {
          onCheckoutComplete(data.order_id);
        }, 2000);
      } else {
        const errorData = await response.json();
        console.error('❌ Order creation failed:', errorData);
        alert('❌ Failed to create order: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('🔴 Network error placing order:', error);
      if (error.message.includes('Failed to fetch')) {
        alert('🔴 Connection Error!\n\n' +
              'Cannot reach the backend server.\n' +
              'Make sure backend is running on http://localhost:5000');
      } else {
        alert('🔴 Error placing order: ' + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout-container">
      <div className="checkout-header">
        <h2>Checkout</h2>
        <button className="btn btn-secondary" onClick={onBack}>Back to Cart</button>
      </div>

      <div className="checkout-content">
        {/* Order Summary */}
        <div className="order-summary-card">
          <h3>Order Summary</h3>
          {cartItems.map((item) => (
            <div key={item.id} className="summary-item">
              <img src={item.image} alt={item.name} className="summary-image" />
              <div className="summary-details">
                <p className="summary-name">{item.name}</p>
                <p className="summary-qty">Qty: {item.quantity}</p>
              </div>
              <p className="summary-price">₹{(item.price * item.quantity).toLocaleString()}</p>
            </div>
          ))}
          
          <div className="summary-totals">
            <div className="total-row">
              <span>Subtotal:</span>
              <span>₹{orderSummary.subtotal.toLocaleString()}</span>
            </div>
            <div className="total-row">
              <span>Shipping:</span>
              <span>{orderSummary.shipping === 0 ? 'FREE' : `₹${orderSummary.shipping}`}</span>
            </div>
            <div className="total-row">
              <span>Tax (18%):</span>
              <span>₹{orderSummary.tax.toLocaleString()}</span>
            </div>
            <div className="total-row total-amount">
              <span>Total:</span>
              <span>₹{orderSummary.total.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Checkout Steps */}
        <div className="checkout-steps">
          {/* Step 1: Address */}
          <div className={`checkout-step ${step >= 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
            <div className="step-header" onClick={() => setStep(1)}>
              <MapPin size={24} />
              <div>
                <h3>Shipping Address</h3>
                {selectedAddress && <p className="step-status">✓ Address selected</p>}
              </div>
            </div>

            {step === 1 && (
              <div className="step-content">
                {selectedAddress ? (
                  <div className="address-display">
                    <p><strong>{selectedAddress.street_address}</strong></p>
                    <p>{selectedAddress.city}, {selectedAddress.state} {selectedAddress.postal_code}</p>
                    <p>{selectedAddress.country}</p>
                  </div>
                ) : (
                  <p className="no-data">No address selected</p>
                )}
                
                <button
                  className="btn btn-primary"
                  onClick={() => setShowAddressManager(true)}
                >
                  {selectedAddress ? 'Change Address' : 'Select Address'}
                </button>
              </div>
            )}
          </div>

          {/* Step 2: Payment */}
          <div className={`checkout-step ${step >= 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
            <div className="step-header" onClick={() => step > 1 && setStep(2)}>
              <CreditCard size={24} />
              <div>
                <h3>Payment Method</h3>
                {paymentMethod && <p className="step-status">✓ Payment method selected</p>}
              </div>
            </div>

            {step === 2 && selectedAddress && (
              <div className="step-content">
                <div className="payment-methods">
                  {['card', 'upi', 'net_banking', 'cod'].map((method) => (
                    <label key={method} className="payment-option">
                      <input
                        type="radio"
                        name="payment"
                        value={method}
                        checked={paymentMethod === method}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                      />
                      <span>{method === 'card' ? 'Credit/Debit Card' : method === 'upi' ? 'UPI' : method === 'net_banking' ? 'Net Banking' : 'Cash on Delivery'}</span>
                    </label>
                  ))}
                </div>

                <button
                  className="btn btn-primary"
                  onClick={handlePlaceOrder}
                  disabled={loading}
                >
                  {loading ? <Loader size={18} /> : <Package size={18} />}
                  {loading ? 'Processing...' : 'Place Order'}
                </button>
              </div>
            )}
          </div>

          {/* Step 3: Confirmation */}
          {step === 3 && (
            <div className="checkout-step active completed">
              <div className="step-header success">
                <div className="success-icon">✓</div>
                <div>
                  <h3>Order Confirmed!</h3>
                  <p className="step-status">Your order has been placed successfully</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <AddressManager
        isOpen={showAddressManager}
        onClose={() => setShowAddressManager(false)}
        onSelectAddress={handleSelectAddress}
        authToken={authToken}
        API_BASE_URL={API_BASE_URL}
      />
    </div>
  );
};

export default Checkout;
