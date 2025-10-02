import { useEffect, useState } from 'react';
import Layout from '../components/layout/Layout';
import { locationsAPI } from '../services/api';
import { MapPin, RefreshCw, Settings } from 'lucide-react';

export default function Locations() {
  const [locations, setLocations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await locationsAPI.getAll();
      setLocations(response.data);
    } catch (error) {
      console.error('Failed to fetch locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await locationsAPI.sync();
      alert('Locations synced successfully');
      fetchLocations();
    } catch (error) {
      console.error('Failed to sync locations:', error);
      alert('Failed to sync locations. Make sure your Google account is connected.');
    } finally {
      setSyncing(false);
    }
  };

  const handleToggleAutoReply = async (locationId: number, currentValue: boolean) => {
    try {
      await locationsAPI.update(locationId, { auto_reply_enabled: !currentValue });
      fetchLocations();
    } catch (error) {
      console.error('Failed to update location:', error);
    }
  };

  const handleToggleAutoPost = async (locationId: number, currentValue: boolean) => {
    try {
      await locationsAPI.update(locationId, { auto_post_enabled: !currentValue });
      fetchLocations();
    } catch (error) {
      console.error('Failed to update location:', error);
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
          <h1 className="text-3xl font-bold text-gray-900">Locations</h1>
          <button
            onClick={handleSync}
            disabled={syncing}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync from Google'}
          </button>
        </div>

        {locations.length === 0 ? (
          <div className="bg-white shadow sm:rounded-lg">
            <div className="px-4 py-12 text-center">
              <MapPin className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No locations</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by syncing your Google Business Profile locations.
              </p>
              <div className="mt-6">
                <button
                  onClick={handleSync}
                  disabled={syncing}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Sync Locations
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {locations.map((location) => (
              <div
                key={location.id}
                className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-primary rounded-md p-3">
                      <MapPin className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-4 flex-1">
                      <h3 className="text-lg font-medium text-gray-900">
                        {location.name}
                      </h3>
                      {location.category && (
                        <p className="text-sm text-gray-500">{location.category}</p>
                      )}
                    </div>
                  </div>

                  <div className="mt-4 space-y-2">
                    {location.address && (
                      <p className="text-sm text-gray-600">{location.address}</p>
                    )}
                    {location.phone && (
                      <p className="text-sm text-gray-600">{location.phone}</p>
                    )}
                  </div>

                  <div className="mt-6 border-t border-gray-200 pt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                      <Settings className="h-4 w-4 mr-1" />
                      Automation Settings
                    </h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-700">Auto Reply</span>
                        <button
                          onClick={() => handleToggleAutoReply(location.id, location.auto_reply_enabled)}
                          className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                            location.auto_reply_enabled ? 'bg-primary' : 'bg-gray-200'
                          }`}
                        >
                          <span
                            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                              location.auto_reply_enabled ? 'translate-x-5' : 'translate-x-0'
                            }`}
                          />
                        </button>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-700">Auto Post</span>
                        <button
                          onClick={() => handleToggleAutoPost(location.id, location.auto_post_enabled)}
                          className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                            location.auto_post_enabled ? 'bg-primary' : 'bg-gray-200'
                          }`}
                        >
                          <span
                            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                              location.auto_post_enabled ? 'translate-x-5' : 'translate-x-0'
                            }`}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
