import React, { useState } from 'react';
import { Star, MessageSquare, Trash2, AlertCircle } from 'lucide-react';

const ReviewSystem = ({ product, user, authToken, API_BASE_URL, onReviewSubmitted }) => {
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [reviewTitle, setReviewTitle] = useState('');
  const [reviewText, setReviewText] = useState('');
  const [loading, setLoading] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [userReview, setUserReview] = useState(null);
  const [error, setError] = useState('');

  React.useEffect(() => {
    fetchReviews();
  }, [product.id]);

  const fetchReviews = async () => {
    try {
      console.log('⭐ Fetching reviews for product:', product.id);
      
      const response = await fetch(`${API_BASE_URL}/reviews/product/${product.id}`, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Reviews fetched:', data.reviews?.length || 0, 'reviews');
        setReviews(data.reviews || []);
        
        // Check if user has already reviewed
        if (user && authToken) {
          const userRev = data.reviews.find(r => r.customer_id === user.customer_id);
          if (userRev) {
            setUserReview(userRev);
          }
        }
      } else {
        const errorData = await response.json();
        console.error('❌ Failed to fetch reviews:', errorData);
      }
    } catch (error) {
      console.error('🔴 Network error fetching reviews:', error);
      if (error.message.includes('Failed to fetch')) {
        setError('🔴 Connection Error: Cannot reach backend server');
      } else {
        setError('Error fetching reviews: ' + error.message);
      }
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    
    if (!user || !authToken) {
      setError('❌ Please log in to write a review');
      return;
    }

    if (!rating || !reviewText) {
      setError('❌ Please provide a rating and review text');
      return;
    }

    setLoading(true);
    try {
      console.log('⭐ Submitting review for product:', product.id);
      console.log('📋 Review data:', { rating, review_title: reviewTitle, review_text: reviewText });
      
      const response = await fetch(`${API_BASE_URL}/reviews`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          product_id: product.id,
          rating,
          review_title: reviewTitle,
          review_text: reviewText
        })
      });

      console.log('Response status:', response.status);

      if (response.ok) {
        console.log('✅ Review submitted successfully');
        setRating(0);
        setReviewTitle('');
        setReviewText('');
        setShowReviewForm(false);
        setError('');
        fetchReviews();
        if (onReviewSubmitted) {
          onReviewSubmitted();
        }
      } else {
        const data = await response.json();
        console.error('❌ Review submission failed:', data);
        setError('❌ ' + (data.error || 'Failed to submit review'));
      }
    } catch (error) {
      console.error('🔴 Network error submitting review:', error);
      if (error.message.includes('Failed to fetch')) {
        setError('🔴 Connection Error: Cannot reach backend server');
      } else {
        setError('🔴 Error submitting review: ' + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteReview = async (reviewId) => {
    if (window.confirm('Delete this review?')) {
      try {
        console.log('🗑️ Deleting review:', reviewId);
        
        const response = await fetch(`${API_BASE_URL}/reviews/${reviewId}`, {
          method: 'DELETE',
          headers: { 
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          }
        });

        console.log('Response status:', response.status);
        
        if (response.ok) {
          console.log('✅ Review deleted successfully');
          fetchReviews();
        } else {
          const errorData = await response.json();
          console.error('❌ Delete failed:', errorData);
          setError('❌ ' + (errorData.error || 'Failed to delete review'));
        }
      } catch (error) {
        console.error('🔴 Network error deleting review:', error);
        if (error.message.includes('Failed to fetch')) {
          setError('🔴 Connection Error: Cannot reach backend server');
        } else {
          setError('🔴 Error: ' + error.message);
        }
      }
    }
  };

  const renderStars = (ratingValue, interactive = false) => {
    return (
      <div className="stars-container">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={interactive ? 24 : 16}
            className={`star ${(interactive ? hoverRating : ratingValue) >= star ? 'filled' : ''}`}
            onClick={() => interactive && setRating(star)}
            onMouseEnter={() => interactive && setHoverRating(star)}
            onMouseLeave={() => interactive && setHoverRating(0)}
            style={{ cursor: interactive ? 'pointer' : 'default' }}
          />
        ))}
      </div>
    );
  };

  const avgRating = reviews.length > 0
    ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
    : 0;

  return (
    <div className="review-system">
      {/* Rating Summary */}
      <div className="rating-summary">
        <div className="rating-display">
          <p className="avg-rating">{avgRating}</p>
          <div className="rating-stars">
            {renderStars(Math.round(avgRating))}
          </div>
          <p className="review-count">({reviews.length} reviews)</p>
        </div>

        {user && authToken && !userReview && (
          <button
            className="btn btn-primary"
            onClick={() => setShowReviewForm(!showReviewForm)}
          >
            <MessageSquare size={18} />
            Write a Review
          </button>
        )}
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <div className="review-form-container">
          <h4>Share Your Review</h4>
          
          {error && (
            <div className="error-message">
              <AlertCircle size={18} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmitReview} className="review-form">
            <div className="form-group">
              <label>Rating</label>
              <div className="rating-input">
                {renderStars(rating, true)}
              </div>
            </div>

            <div className="form-group">
              <label>Review Title</label>
              <input
                type="text"
                value={reviewTitle}
                onChange={(e) => setReviewTitle(e.target.value)}
                placeholder="e.g., Excellent quality!"
                maxLength={100}
              />
            </div>

            <div className="form-group">
              <label>Your Review</label>
              <textarea
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                placeholder="Share your experience with this product..."
                rows={4}
                required
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Review'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowReviewForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Reviews List */}
      <div className="reviews-list">
        <h4>Customer Reviews ({reviews.length})</h4>
        
        {reviews.length === 0 ? (
          <p className="no-reviews">No reviews yet. Be the first to review!</p>
        ) : (
          reviews.map((review) => (
            <div key={review.review_id} className="review-item">
              <div className="review-header">
                <div className="reviewer-info">
                  <p className="reviewer-name">
                    {review.first_name} {review.last_name}
                  </p>
                  <div className="review-meta">
                    {renderStars(review.rating)}
                    <span className="review-date">
                      {new Date(review.review_date).toLocaleDateString('en-IN')}
                    </span>
                  </div>
                </div>

                {user && user.customer_id === review.customer_id && (
                  <button
                    className="btn btn-small btn-danger"
                    onClick={() => handleDeleteReview(review.review_id)}
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>

              {review.review_title && (
                <p className="review-title">
                  <strong>{review.review_title}</strong>
                </p>
              )}

              <p className="review-text">{review.review_text}</p>

              {review.is_verified && (
                <span className="verified-badge">✓ Verified Purchase</span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ReviewSystem;
