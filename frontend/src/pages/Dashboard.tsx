import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { locationsAPI, postsAPI, reviewsAPI } from '../services/api';
import { MapPin, FileText, Star, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    locations: 0,
    posts: 0,
    reviews: 0,
    avgRating: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [locationsRes, postsRes, reviewsRes] = await Promise.all([
        locationsAPI.getAll(),
        postsAPI.getAll(),
        reviewsAPI.getAll(),
      ]);

      const reviews = reviewsRes.data;
      const avgRating = reviews.length > 0
        ? reviews.reduce((acc: number, r: any) => acc + r.rating, 0) / reviews.length
        : 0;

      setStats({
        locations: locationsRes.data.length,
        posts: postsRes.data.length,
        reviews: reviews.length,
        avgRating: Math.round(avgRating * 10) / 10,
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      name: 'Locations',
      value: stats.locations,
      icon: MapPin,
      color: 'bg-blue-500',
      link: '/locations',
    },
    {
      name: 'Posts',
      value: stats.posts,
      icon: FileText,
      color: 'bg-green-500',
      link: '/posts',
    },
    {
      name: 'Reviews',
      value: stats.reviews,
      icon: Star,
      color: 'bg-yellow-500',
      link: '/reviews',
    },
    {
      name: 'Avg Rating',
      value: stats.avgRating.toFixed(1),
      icon: TrendingUp,
      color: 'bg-purple-500',
      link: '/reviews',
    },
  ];

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
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {statCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <Link
                key={stat.name}
                to={stat.link}
                className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="p-5">
                  <div className="flex items-center">
                    <div className={`flex-shrink-0 ${stat.color} rounded-md p-3`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          {stat.name}
                        </dt>
                        <dd className="text-3xl font-semibold text-gray-900">
                          {stat.value}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Link
              to="/posts/new"
              className="inline-flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90"
            >
              Create New Post
            </Link>
            <Link
              to="/locations"
              className="inline-flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Manage Locations
            </Link>
            <Link
              to="/reviews"
              className="inline-flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              View Reviews
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}
