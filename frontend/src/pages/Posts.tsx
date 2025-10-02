import { useEffect, useState } from 'react';
import Layout from '../components/layout/Layout';
import { postsAPI, locationsAPI } from '../services/api';
import { Plus, Send, Trash2, Sparkles } from 'lucide-react';
import { format } from 'date-fns';

export default function Posts() {
  const [posts, setPosts] = useState<any[]>([]);
  const [locations, setLocations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState('');
  const [content, setContent] = useState('');
  const [topic, setTopic] = useState('');
  const [useAI, setUseAI] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [postsRes, locationsRes] = await Promise.all([
        postsAPI.getAll(),
        locationsAPI.getAll(),
      ]);
      setPosts(postsRes.data);
      setLocations(locationsRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (useAI) {
        await postsAPI.generate({
          location_id: parseInt(selectedLocation),
          topic: topic || undefined,
        });
      } else {
        await postsAPI.create({
          location_id: parseInt(selectedLocation),
          content,
        });
      }
      setShowCreateModal(false);
      setContent('');
      setTopic('');
      setSelectedLocation('');
      setUseAI(false);
      fetchData();
    } catch (error) {
      console.error('Failed to create post:', error);
    }
  };

  const handlePublish = async (postId: number) => {
    try {
      await postsAPI.publish(postId);
      alert('Post queued for publishing');
      fetchData();
    } catch (error) {
      console.error('Failed to publish post:', error);
    }
  };

  const handleDelete = async (postId: number) => {
    if (confirm('Are you sure you want to delete this post?')) {
      try {
        await postsAPI.delete(postId);
        fetchData();
      } catch (error) {
        console.error('Failed to delete post:', error);
      }
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Posts</h1>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Post
          </button>
        </div>

        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {posts.length === 0 ? (
              <li className="px-6 py-12 text-center text-gray-500">
                No posts yet. Create your first post!
              </li>
            ) : (
              posts.map((post) => (
                <li key={post.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900">
                          {post.content.substring(0, 100)}
                          {post.content.length > 100 && '...'}
                        </p>
                        <div className="ml-2 flex-shrink-0 flex">
                          <span
                            className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              post.status === 'PUBLISHED'
                                ? 'bg-green-100 text-green-800'
                                : post.status === 'SCHEDULED'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {post.status}
                          </span>
                        </div>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <span>
                          {post.ai_generated && (
                            <span className="inline-flex items-center mr-2">
                              <Sparkles className="h-3 w-3 mr-1" />
                              AI Generated
                            </span>
                          )}
                          Created {format(new Date(post.created_at), 'MMM d, yyyy')}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4 flex space-x-2">
                      {post.status === 'DRAFT' && (
                        <button
                          onClick={() => handlePublish(post.id)}
                          className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                        >
                          <Send className="h-4 w-4 mr-1" />
                          Publish
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(post.id)}
                        className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>

        {/* Create Post Modal */}
        {showCreateModal && (
          <div className="fixed z-10 inset-0 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
              <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowCreateModal(false)}></div>
              <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
                <form onSubmit={handleCreatePost}>
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Create New Post
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Location
                      </label>
                      <select
                        required
                        value={selectedLocation}
                        onChange={(e) => setSelectedLocation(e.target.value)}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
                      >
                        <option value="">Select a location</option>
                        {locations.map((loc) => (
                          <option key={loc.id} value={loc.id}>
                            {loc.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={useAI}
                        onChange={(e) => setUseAI(e.target.checked)}
                        className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Generate with AI
                      </label>
                    </div>

                    {useAI ? (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Topic (optional)
                        </label>
                        <input
                          type="text"
                          value={topic}
                          onChange={(e) => setTopic(e.target.value)}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
                          placeholder="e.g., New product launch"
                        />
                      </div>
                    ) : (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Content
                        </label>
                        <textarea
                          required
                          value={content}
                          onChange={(e) => setContent(e.target.value)}
                          rows={4}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
                          placeholder="Write your post content..."
                        />
                      </div>
                    )}
                  </div>

                  <div className="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                    <button
                      type="submit"
                      className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary text-base font-medium text-white hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary sm:col-start-2 sm:text-sm"
                    >
                      Create
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateModal(false)}
                      className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary sm:mt-0 sm:col-start-1 sm:text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
