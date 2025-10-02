import { useEffect, useState } from 'react';
import Layout from '../components/layout/Layout';
import { reviewsAPI } from '../services/api';
import { Star, MessageSquare, Sparkles } from 'lucide-react';
import { format } from 'date-fns';

export default function Reviews() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReview, setSelectedReview] = useState<any>(null);
  const [replyText, setReplyText] = useState('');
  const [generatingReply, setGeneratingReply] = useState(false);

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const response = await reviewsAPI.getAll();
      setReviews(response.data);
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReply = async (reviewId: number) => {
    setGeneratingReply(true);
    try {
      const response = await reviewsAPI.generateReply(reviewId, 'professional');
      setReplyText(response.data.reply_text);
    } catch (error) {
      console.error('Failed to generate reply:', error);
    } finally {
      setGeneratingReply(false);
    }
  };

  const handleSubmitReply = async (reviewId: number) => {
    try {
      await reviewsAPI.reply(reviewId, replyText);
      setSelectedReview(null);
      setReplyText('');
      fetchReviews();
    } catch (error) {
      console.error('Failed to submit reply:', error);
    }
  };

  const handleSync = async () => {
    try {
      await reviewsAPI.sync();
      alert('Reviews sync started');
      setTimeout(fetchReviews, 2000);
    } catch (error) {
      console.error('Failed to sync reviews:', error);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-4 w-4 ${
              star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="px-4 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Reviews</h1>
          <button
            onClick={handleSync}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90"
          >
            Sync Reviews
          </button>
        </div>

        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {reviews.length === 0 ? (
              <li className="px-6 py-12 text-center text-gray-500">
                No reviews yet. Sync your reviews from Google Business Profile.
              </li>
            ) : (
              reviews.map((review) => (
                <li key={review.id} className="px-6 py-4">
                  <div className="flex items-start space-x-4">
                    {review.reviewer_profile_photo && (
                      <img
                        src={review.reviewer_profile_photo}
                        alt={review.reviewer_name}
                        className="h-10 w-10 rounded-full"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900">
                          {review.reviewer_name}
                        </p>
                        <div className="ml-2 flex items-center">
                          {renderStars(review.rating)}
                        </div>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {format(new Date(review.review_created_at), 'MMM d, yyyy')}
                      </p>
                      {review.comment && (
                        <p className="mt-2 text-sm text-gray-700">{review.comment}</p>
                      )}
                      
                      {review.reply_text ? (
                        <div className="mt-3 bg-gray-50 rounded-md p-3">
                          <div className="flex items-center text-sm text-gray-500 mb-1">
                            <MessageSquare className="h-4 w-4 mr-1" />
                            Your reply
                            {review.ai_generated_reply && (
                              <span className="ml-2 inline-flex items-center">
                                <Sparkles className="h-3 w-3 mr-1" />
                                AI Generated
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-700">{review.reply_text}</p>
                        </div>
                      ) : (
                        <button
                          onClick={() => setSelectedReview(review)}
                          className="mt-3 inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                        >
                          <MessageSquare className="h-4 w-4 mr-1" />
                          Reply
                        </button>
                      )}
                    </div>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>

        {/* Reply Modal */}
        {selectedReview && (
          <div className="fixed z-10 inset-0 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
              <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setSelectedReview(null)}></div>
              <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
                <div>
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Reply to {selectedReview.reviewer_name}
                  </h3>
                  
                  <div className="mb-4">
                    <div className="flex items-center mb-2">
                      {renderStars(selectedReview.rating)}
                    </div>
                    {selectedReview.comment && (
                      <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-md">
                        {selectedReview.comment}
                      </p>
                    )}
                  </div>

                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Your Reply
                      </label>
                      <button
                        onClick={() => handleGenerateReply(selectedReview.id)}
                        disabled={generatingReply}
                        className="inline-flex items-center px-2 py-1 text-xs font-medium text-primary hover:text-primary/90"
                      >
                        <Sparkles className="h-3 w-3 mr-1" />
                        {generatingReply ? 'Generating...' : 'Generate with AI'}
                      </button>
                    </div>
                    <textarea
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      rows={4}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
                      placeholder="Write your reply..."
                    />
                  </div>

                  <div className="sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                    <button
                      onClick={() => handleSubmitReply(selectedReview.id)}
                      disabled={!replyText}
                      className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary text-base font-medium text-white hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary sm:col-start-2 sm:text-sm disabled:opacity-50"
                    >
                      Send Reply
                    </button>
                    <button
                      onClick={() => {
                        setSelectedReview(null);
                        setReplyText('');
                      }}
                      className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary sm:mt-0 sm:col-start-1 sm:text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
