import React, { useState, useEffect } from 'react';
import { MapPin, Plus, Edit2, Trash2, Check } from 'lucide-react';

const AddressManager = ({ isOpen, onClose, onSelectAddress, authToken, API_BASE_URL }) => {
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    street_address: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    address_type: 'both',
    set_as_shipping: false,
    set_as_billing: false
  });
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchAddresses();
    }
  }, [isOpen]);

  const fetchAddresses = async () => {
    try {
      setLoading(true);
      console.log('Fetching addresses from:', `${API_BASE_URL}/addresses`);
      console.log('Using auth token:', authToken ? 'Present' : 'Missing');
      
      const response = await fetch(`${API_BASE_URL}/addresses`, {
        method: 'GET',
        headers: { 
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      const data = await response.json();
      console.log('Response data:', data);
      
      if (response.ok) {
        setAddresses(data.addresses || []);
        console.log('Addresses updated successfully:', data.addresses?.length || 0, 'addresses');
      } else {
        console.error('Error response from server:', data);
        alert('Error fetching addresses: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Network error fetching addresses:', error);
      console.error('Error details:', error.message, error.stack);
      alert('Network Error: ' + error.message + '\n\nMake sure the backend server is running on http://localhost:5000');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.street_address || !formData.city || !formData.state || !formData.postal_code) {
      alert('❌ Please fill in all required fields:\n- Street Address\n- City\n- State\n- Postal Code');
      return;
    }

    try {
      setLoading(true);
      const submitURL = `${API_BASE_URL}/addresses`;
      console.log('📤 Submitting to:', submitURL);
      console.log('📋 Address data:', formData);
      console.log('🔑 Auth token present:', authToken ? 'Yes' : 'No');
      
      const response = await fetch(submitURL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      console.log('📥 Response status:', response.status, response.statusText);
      
      const responseData = await response.json();
      console.log('📥 Response body:', responseData);

      if (response.ok) {
        console.log('✅ Address created successfully:', responseData);
        alert('✅ Address added successfully!\n\nAddress ID: ' + responseData.address_id);
        setFormData({
          street_address: '',
          city: '',
          state: '',
          postal_code: '',
          country: 'India',
          address_type: 'both',
          set_as_shipping: false,
          set_as_billing: false
        });
        setShowForm(false);
        await fetchAddresses();
      } else {
        const errorMsg = responseData.error || 'Failed to add address';
        console.error('❌ Server error:', errorMsg);
        alert('❌ Error: ' + errorMsg);
      }
    } catch (error) {
      console.error('🔴 Network error:', error);
      console.error('Error type:', error.constructor.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      
      if (error.message.includes('Failed to fetch')) {
        alert('🔴 Connection Error!\n\n' +
              'Cannot reach the backend server.\n\n' +
              'Make sure:\n' +
              '1. Backend is running: python backend/app.py\n' +
              '2. Server is on: http://localhost:5000\n' +
              '3. No firewall blocking port 5000\n\n' +
              'Error: ' + error.message);
      } else {
        alert('🔴 Error: ' + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (addressId) => {
    if (window.confirm('Delete this address?')) {
      try {
        const response = await fetch(`${API_BASE_URL}/addresses/${addressId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (response.ok) {
          fetchAddresses();
        }
      } catch (error) {
        console.error('Error deleting address:', error);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Manage Addresses</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {showForm ? (
            <form onSubmit={handleSubmit} className="address-form">
              <input
                type="text"
                placeholder="Street Address"
                value={formData.street_address}
                onChange={(e) => setFormData({...formData, street_address: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="City"
                value={formData.city}
                onChange={(e) => setFormData({...formData, city: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="State"
                value={formData.state}
                onChange={(e) => setFormData({...formData, state: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Postal Code"
                value={formData.postal_code}
                onChange={(e) => setFormData({...formData, postal_code: e.target.value})}
                required
              />
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.set_as_shipping}
                  onChange={(e) => setFormData({...formData, set_as_shipping: e.target.checked})}
                />
                Set as shipping address
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.set_as_billing}
                  onChange={(e) => setFormData({...formData, set_as_billing: e.target.checked})}
                />
                Set as billing address
              </label>
              <button type="submit" className="btn btn-primary">Save Address</button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>
            </form>
          ) : (
            <>
              <button
                className="btn btn-primary"
                onClick={() => setShowForm(true)}
                style={{ marginBottom: '1rem' }}
              >
                <Plus size={18} /> Add New Address
              </button>

              {loading ? (
                <p>Loading addresses...</p>
              ) : addresses.length === 0 ? (
                <p>No addresses saved. Add one to get started.</p>
              ) : (
                <div className="addresses-list">
                  {addresses.map((addr) => (
                    <div key={addr.address_id} className="address-card">
                      <div className="address-info">
                        <MapPin size={18} />
                        <div>
                          <p className="address-line">{addr.street_address}</p>
                          <p className="address-line">{addr.city}, {addr.state} {addr.postal_code}</p>
                          <p className="address-line">{addr.country}</p>
                        </div>
                      </div>
                      <div className="address-actions">
                        <button
                          className="btn btn-small btn-primary"
                          onClick={() => onSelectAddress(addr)}
                        >
                          <Check size={16} /> Select
                        </button>
                        <button
                          className="btn btn-small btn-danger"
                          onClick={() => handleDelete(addr.address_id)}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AddressManager;
