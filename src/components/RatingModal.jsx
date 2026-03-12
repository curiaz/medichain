import React, { useState } from "react";
import { X, Star } from "lucide-react";
import "../assets/styles/RatingModal.css";

const RatingModal = ({ isOpen, onClose, appointmentId, doctorName, onSubmit, existingRating = null }) => {
  const [rating, setRating] = useState(existingRating?.rating || 0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [comment, setComment] = useState(existingRating?.comment || "");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (rating === 0) {
      setError("Please select a rating");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await onSubmit({
        appointment_id: appointmentId,
        rating: rating,
        comment: comment.trim(),
      });
      onClose();
    } catch (err) {
      setError(err.message || "Failed to submit rating. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleStarClick = (value) => {
    setRating(value);
    setError(null);
  };

  const handleStarHover = (value) => {
    setHoveredRating(value);
  };

  const handleStarLeave = () => {
    setHoveredRating(0);
  };

  return (
    <div className="rating-modal-overlay" onClick={onClose}>
      <div className="rating-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="rating-modal-header">
          <h2>Rate Your Experience</h2>
          <button className="rating-modal-close" onClick={onClose} aria-label="Close">
            <X size={24} />
          </button>
        </div>

        <div className="rating-modal-body">
          <div className="rating-doctor-info">
            <p>How was your consultation with</p>
            <h3>Dr. {doctorName}</h3>
          </div>

          {error && (
            <div className="rating-error">
              {error}
            </div>
          )}

          <div className="rating-stars-container">
            <label>Rating *</label>
            <div className="rating-stars">
              {[1, 2, 3, 4, 5].map((value) => (
                <button
                  key={value}
                  type="button"
                  className="rating-star-btn"
                  onClick={() => handleStarClick(value)}
                  onMouseEnter={() => handleStarHover(value)}
                  onMouseLeave={handleStarLeave}
                  aria-label={`Rate ${value} star${value !== 1 ? 's' : ''}`}
                >
                  <Star
                    size={40}
                    className={`rating-star ${
                      value <= (hoveredRating || rating) ? 'filled' : 'empty'
                    }`}
                    fill={value <= (hoveredRating || rating) ? '#FFD700' : 'none'}
                    stroke={value <= (hoveredRating || rating) ? '#FFD700' : '#ccc'}
                  />
                </button>
              ))}
            </div>
            {rating > 0 && (
              <p className="rating-text">
                {rating === 1 && "Poor"}
                {rating === 2 && "Fair"}
                {rating === 3 && "Good"}
                {rating === 4 && "Very Good"}
                {rating === 5 && "Excellent"}
              </p>
            )}
          </div>

          <div className="rating-comment-container">
            <label htmlFor="rating-comment">Comment (Optional)</label>
            <textarea
              id="rating-comment"
              className="rating-comment-input"
              placeholder="Share your experience with this doctor..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              maxLength={500}
            />
            <span className="rating-comment-count">{comment.length}/500</span>
          </div>
        </div>

        <div className="rating-modal-footer">
          <button
            className="rating-cancel-btn"
            onClick={onClose}
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            className="rating-submit-btn"
            onClick={handleSubmit}
            disabled={submitting || rating === 0}
          >
            {submitting ? "Submitting..." : existingRating ? "Update Rating" : "Submit Rating"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RatingModal;




