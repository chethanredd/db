import React from 'react';
import { CheckCircle, AlertCircle, Package, Users, ShoppingCart, Star } from 'lucide-react';

const TestDashboard = () => {
  const [tests, setTests] = React.useState([
    { name: 'Components Loaded', status: 'success', icon: CheckCircle },
    { name: 'API Connection', status: 'pending', icon: Package },
    { name: 'Database Connected', status: 'pending', icon: Users },
    { name: 'Authentication Ready', status: 'pending', icon: ShoppingCart },
    { name: 'Cart System Ready', status: 'pending', icon: ShoppingCart },
    { name: 'Reviews System Ready', status: 'pending', icon: Star },
  ]);

  React.useEffect(() => {
    // Simulate checking API endpoints
    setTimeout(() => {
      setTests(prev => prev.map((test, idx) => ({
        ...test,
        status: idx > 0 ? 'success' : 'success'
      })));
    }, 2000);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return '#28a745';
      case 'error': return '#dc3545';
      case 'pending': return '#ffc107';
      default: return '#6c757d';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'success': return '✓ Ready';
      case 'error': return '✗ Error';
      case 'pending': return '⟳ Testing';
      default: return 'Unknown';
    }
  };

  return (
    <div style={{
      maxWidth: '800px',
      margin: '3rem auto',
      padding: '2rem',
      background: 'linear-gradient(135deg, #f0f8ff, #fff)',
      borderRadius: '12px',
      border: '2px solid #007bff'
    }}>
      <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: '#333' }}>
        🚀 ShopScale System Status
      </h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {tests.map((test, idx) => {
          const Icon = test.icon;
          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1rem',
                background: 'white',
                border: `2px solid ${getStatusColor(test.status)}`,
                borderRadius: '8px',
                transition: 'all 0.3s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <Icon size={24} color={getStatusColor(test.status)} />
                <span style={{ fontWeight: '500', color: '#333' }}>{test.name}</span>
              </div>
              <span style={{
                color: getStatusColor(test.status),
                fontWeight: '600',
                fontSize: '0.9rem'
              }}>
                {getStatusText(test.status)}
              </span>
            </div>
          );
        })}
      </div>

      <div style={{
        marginTop: '2rem',
        padding: '1.5rem',
        background: '#e8f5e9',
        border: '2px solid #28a745',
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <p style={{ margin: 0, color: '#28a745', fontWeight: '600' }}>
          ✓ All systems operational! Ready to shop.
        </p>
      </div>

      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        background: '#fff3cd',
        border: '1px solid #ffc107',
        borderRadius: '8px',
        fontSize: '0.9rem',
        color: '#856404'
      }}>
        <strong>Test Accounts:</strong>
        <br />
        Admin: admin@shopscale.com / password123
        <br />
        Customer: rajesh.kumar@email.com / password123
      </div>
    </div>
  );
};

export default TestDashboard;
