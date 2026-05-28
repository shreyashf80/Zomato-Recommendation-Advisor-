import React, { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Sample fallback food/dining images to cycle through for high-quality card graphics
const CARD_IMAGES = [
  'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1552566626-52f8b828add9?w=600&auto=format&fit=crop&q=80'
];

export default function App() {
  // Form states
  const [locations, setLocations] = useState([]);
  const [cuisines, setCuisines] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedCuisine, setSelectedCuisine] = useState('');
  const [budget, setBudget] = useState('medium'); // low | medium | high
  const [minRating, setMinRating] = useState(3.5);
  const [topK, setTopK] = useState(6); // Default 6 looks best in a 3-column grid
  const [additionalPrefs, setAdditionalPrefs] = useState('');

  // App running states
  const [metaLoading, setMetaLoading] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch locations & cuisines on load
  useEffect(() => {
    async function fetchMetadata() {
      try {
        setMetaLoading(true);
        setErrorMsg('');
        
        const locRes = await fetch(`${API_BASE_URL}/metadata/locations`);
        if (!locRes.ok) throw new Error('Failed to fetch locations');
        const locData = await locRes.json();
        setLocations(locData);
        if (locData.length > 0) {
          const defaultLoc = locData.find(l => l.toLowerCase().includes('btm') || l.toLowerCase().includes('connaught')) || locData[0];
          setSelectedLocation(defaultLoc);
        }

        const cuisRes = await fetch(`${API_BASE_URL}/metadata/cuisines`);
        if (!cuisRes.ok) throw new Error('Failed to fetch cuisines');
        const cuisData = await cuisRes.json();
        setCuisines(cuisData);
        if (cuisData.length > 0) {
          const defaultCuis = cuisData.find(c => c.toLowerCase() === 'chinese' || c.toLowerCase() === 'north indian') || cuisData[0];
          setSelectedCuisine(defaultCuis);
        }
      } catch (err) {
        console.error(err);
        setErrorMsg('Could not connect to the Zomato AI server at ' + API_BASE_URL + '. Please verify your server connection or CORS settings.');
      } finally {
        setMetaLoading(false);
      }
    }
    fetchMetadata();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedLocation || !selectedCuisine) {
      setErrorMsg('Please select both a location and a cuisine.');
      return;
    }

    try {
      setIsLoading(true);
      setErrorMsg('');
      setResults(null);

      const response = await fetch(`${API_BASE_URL}/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          location: selectedLocation,
          cuisine: selectedCuisine,
          budget: budget,
          min_rating: parseFloat(minRating),
          top_k: parseInt(topK),
          additional_preferences: additionalPrefs.trim() || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch recommendations');
      }

      const data = await response.json();
      setResults(data);
      
      // Smooth scroll down to results section
      setTimeout(() => {
        const target = document.getElementById('results-section');
        if (target) {
          target.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'An error occurred while compiling your recommendations.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-bright text-on-surface flex flex-col justify-between">
      
      {/* Top Header Bar (Full Width Container) */}
      <header className="bg-surface-white border-b border-border-light shadow-sm sticky top-0 z-50">
        <div className="flex justify-between items-center w-full max-w-[1200px] mx-auto px-gutter h-touch-target">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">Z</span>
            </div>
            <h1 className="text-headline-md font-headline-md font-extrabold text-primary tracking-tighter">Zomato AI</h1>
          </div>
        </div>
      </header>

      {/* Main Content (Wide Container - max-w-[1200px]) */}
      <main className="w-full max-w-[1200px] mx-auto px-gutter py-section-gap flex-grow">
        
        {/* Welcome Section */}
        <div className="text-center mb-section-gap">
          <h2 className="font-headline-lg text-headline-lg text-deep-charcoal mb-2 md:block hidden">
            Zomato AI Recommendation Advisor
          </h2>
          <h2 className="font-headline-lg-mobile text-headline-lg-mobile text-deep-charcoal mb-2 md:hidden">
            Zomato AI Advisor
          </h2>
          <p className="font-body-lg text-body-lg text-on-surface-variant">
            Sophisticated culinary curation powered by real-time Zomato data.
          </p>
        </div>

        {/* Global Error Banner */}
        {errorMsg && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md mb-6 flex items-start gap-3">
            <span className="material-symbols-outlined text-red-500">error</span>
            <div className="text-sm text-red-700 font-medium">{errorMsg}</div>
          </div>
        )}

        {/* Preferences Control Form (Wide, Horizontal Grid Style) */}
        <section className="bg-surface-white rounded-xl border border-border-light shadow-[0px_2px_8px_rgba(28,28,28,0.08)] p-6 mb-section-gap">
          <form className="space-y-6" onSubmit={handleSubmit}>
            
            {/* Row 1: Dropdowns & Budget Selector (3 columns on desktop) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Location Selector */}
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-on-surface-variant uppercase block">
                  Current Location
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">
                    location_on
                  </span>
                  <select
                    disabled={metaLoading}
                    value={selectedLocation}
                    onChange={(e) => setSelectedLocation(e.target.value)}
                    className="w-full h-touch-target pl-10 pr-4 bg-white border border-border-light rounded-xl focus:ring-2 focus:ring-primary focus:border-primary outline-none appearance-none cursor-pointer"
                  >
                    {metaLoading ? (
                      <option>Loading locations...</option>
                    ) : (
                      locations.map((loc) => (
                        <option key={loc} value={loc}>
                          {loc}
                        </option>
                      ))
                    )}
                  </select>
                </div>
              </div>

              {/* Cuisine Selector */}
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-on-surface-variant uppercase block">
                  Cuisine Preference
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">
                    restaurant_menu
                  </span>
                  <select
                    disabled={metaLoading}
                    value={selectedCuisine}
                    onChange={(e) => setSelectedCuisine(e.target.value)}
                    className="w-full h-touch-target pl-10 pr-4 bg-white border border-border-light rounded-xl focus:ring-2 focus:ring-primary focus:border-primary outline-none appearance-none cursor-pointer capitalize"
                  >
                    {metaLoading ? (
                      <option>Loading cuisines...</option>
                    ) : (
                      cuisines.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))
                    )}
                  </select>
                </div>
              </div>

              {/* Budget Range Button Pills */}
              <div className="space-y-2">
                <label className="font-label-caps text-label-caps text-on-surface-variant uppercase block">
                  Budget Range
                </label>
                <div className="flex gap-2">
                  {[
                    { key: 'low', label: 'Low' },
                    { key: 'medium', label: 'Medium' },
                    { key: 'high', label: 'High' }
                  ].map((b) => (
                    <button
                      key={b.key}
                      type="button"
                      onClick={() => setBudget(b.key)}
                      className={`flex-1 h-touch-target font-label-caps text-label-caps rounded-xl transition-all duration-300 ${
                        budget === b.key
                          ? 'border-2 border-primary bg-ai-tint text-primary font-bold'
                          : 'border border-border-light bg-white text-deep-charcoal hover:bg-slate-50'
                      }`}
                    >
                      {b.label}
                    </button>
                  ))}
                </div>
              </div>

            </div>

            {/* Row 2: Sliders (2 columns on desktop) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Rating Slider */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">
                    Minimum Rating
                  </label>
                  <span className="flex items-center text-primary font-bold">
                    <span className="material-symbols-outlined text-[18px] mr-1" style={{ fontVariationSettings: "'FILL' 1" }}>
                      star
                    </span> 
                    {minRating.toFixed(1)}+
                  </span>
                </div>
                <input
                  type="range"
                  min="3.0"
                  max="5.0"
                  step="0.1"
                  value={minRating}
                  onChange={(e) => setMinRating(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-surface-container-highest rounded-lg appearance-none cursor-pointer custom-slider"
                />
              </div>

              {/* Count Slider */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">
                    Recommendations
                  </label>
                  <span className="text-primary font-bold">{topK} Results</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="12"
                  step="1"
                  value={topK}
                  onChange={(e) => setTopK(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-surface-container-highest rounded-lg appearance-none cursor-pointer custom-slider"
                />
              </div>

            </div>

            {/* Row 3: Special Requests Textarea & Search Action (2/3 vs 1/3 ratio on desktop) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Special Requests */}
              <div className="space-y-2 md:col-span-2">
                <label className="font-label-caps text-label-caps text-on-surface-variant uppercase block">
                  Special Requests / Occasion
                </label>
                <textarea
                  value={additionalPrefs}
                  onChange={(e) => setAdditionalPrefs(e.target.value)}
                  className="w-full p-3 border border-border-light rounded-xl focus:ring-2 focus:ring-primary focus:border-primary outline-none min-h-[64px] font-body-sm text-body-sm bg-white"
                  placeholder="e.g., 'Pet-friendly terrace for a birthday dinner' or 'Quiet spot for a business meeting'"
                />
              </div>

              {/* Submit CTA Button */}
              <div className="space-y-2 md:col-span-1">
                <label className="font-label-caps text-label-caps text-transparent block select-none hidden md:block">
                  Search
                </label>
                <button
                  type="submit"
                  disabled={isLoading || metaLoading}
                  className="w-full h-touch-target bg-primary text-white rounded-xl font-headline-md hover:opacity-95 transition-all active:scale-95 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                >
                  {isLoading ? (
                    <>
                      <span className="material-symbols-outlined animate-spin">refresh</span>
                      Consulting AI...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined">search</span>
                      Find My Perfect Meal
                    </>
                  )}
                </button>
              </div>

            </div>

          </form>
        </section>

        {/* Loading Skeleton Panel (Grid Format) */}
        {isLoading && (
          <div className="space-y-6">
            <div className="bg-gray-100 h-24 rounded-r-xl border-l-4 border-gray-300 p-6 animate-pulse"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
              <div className="bg-white border border-border-light h-96 rounded-xl"></div>
              <div className="bg-white border border-border-light h-96 rounded-xl"></div>
              <div className="bg-white border border-border-light h-96 rounded-xl"></div>
            </div>
          </div>
        )}

        {/* Results Container (Summary Block + Multi-column Card Grid) */}
        {results && (
          <div className="space-y-6" id="results-section">
            
            {/* AI Summary Banner (Full Width) */}
            {results.summary && (
              <div className="bg-ai-tint border-l-4 border-primary p-6 rounded-r-xl flex gap-4 items-start border border-y-border-light border-r-border-light shadow-sm w-full">
                <span className="material-symbols-outlined text-primary mt-1" style={{ fontVariationSettings: "'FILL' 1" }}>
                  auto_awesome
                </span>
                <div>
                  <h3 className="font-headline-md text-headline-md text-deep-charcoal mb-1">
                    AI Recommendation Summary
                  </h3>
                  <p className="font-ai-verdict text-ai-verdict text-on-surface-variant">
                    {results.summary}
                  </p>
                </div>
              </div>
            )}

            {/* Restaurant Cards Grid (2-3 Cards per row on desktop) */}
            {results.recommendations.length === 0 ? (
              <div className="text-center py-12 bg-white border border-border-light rounded-xl w-full">
                <span className="material-symbols-outlined text-4xl text-cool-gray mb-2">restaurant_menu</span>
                <p className="text-cool-gray">No matching restaurants found. Try broadening your location or budget preferences.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.recommendations.map((rec) => {
                  const rest = rec.restaurant;
                  const votes = rest.metadata?.votes || 0;
                  const restType = rest.metadata?.rest_type || 'Casual Dining';
                  const address = rest.metadata?.address || 'Location details available in store.';
                  const url = rest.metadata?.url || '#';
                  
                  // Color-code rating pills
                  const isHighRating = rest.rating >= 4.0;
                  
                  // Select consistent photo based on restaurant ID hash
                  const imgIndex = Math.abs(rest.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)) % CARD_IMAGES.length;
                  const cardImg = CARD_IMAGES[imgIndex];

                  return (
                    <article
                      key={rest.id}
                      className="bg-surface-white border border-border-light rounded-xl shadow-[0px_2px_8px_rgba(28,28,28,0.08)] overflow-hidden transition-all hover:-translate-y-1.5 hover:shadow-xl group flex flex-col h-full"
                    >
                      {/* Top: Cover Photo */}
                      <div className="w-full h-48 overflow-hidden relative shrink-0">
                        <img
                          alt={rest.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                          src={cardImg}
                        />
                        <div className="absolute top-0 left-0 bg-primary text-white px-4 py-2 font-headline-md shadow-md rounded-br-lg">
                          #{rec.rank}
                        </div>
                      </div>

                      {/* Bottom: Card Content (Pushed apart using flex justify-between) */}
                      <div className="p-5 flex-grow flex flex-col justify-between space-y-4">
                        
                        <div className="space-y-3">
                          {/* Name & Rating Pill */}
                          <div className="flex justify-between items-start gap-2">
                            <h3 className="font-headline-md text-headline-md text-deep-charcoal leading-tight">
                              {rest.name}
                            </h3>
                            <div
                              style={{ backgroundColor: isHighRating ? '#24963F' : '#FFBA43' }}
                              className="text-white px-2 py-1 rounded text-label-caps flex items-center shrink-0 shadow-sm"
                            >
                              {rest.rating.toFixed(1)} 
                              <span className="material-symbols-outlined text-[14px] ml-1" style={{ fontVariationSettings: "'FILL' 1" }}>
                                star
                              </span>
                            </div>
                          </div>

                          {/* Cuisine Tags */}
                          <div className="flex flex-wrap gap-1.5">
                            {rest.cuisines.slice(0, 3).map((c) => (
                              <span key={c} className="bg-surface-container-low px-2.5 py-0.5 rounded-full text-label-caps text-on-surface-variant capitalize">
                                {c}
                              </span>
                            ))}
                            <span className="bg-surface-container-low px-2.5 py-0.5 rounded-full text-label-caps text-on-surface-variant">
                              {restType}
                            </span>
                          </div>

                          {/* Metadata Details */}
                          <div className="flex flex-col gap-1 text-on-surface-variant font-body-sm pt-1 border-t border-gray-100">
                            <div className="flex items-center gap-1.5">
                              <span className="material-symbols-outlined text-[16px] text-cool-gray">location_on</span>
                              <span className="truncate">{rest.location}</span>
                            </div>
                            {rest.estimated_cost && (
                              <div className="flex items-center gap-1.5">
                                <span className="material-symbols-outlined text-[16px] text-cool-gray">payments</span>
                                <span>₹{rest.estimated_cost.toLocaleString('en-IN')} for two</span>
                              </div>
                            )}
                            <div className="text-[11px] text-cool-gray pl-5">
                              ({votes.toLocaleString('en-IN')} votes)
                            </div>
                          </div>

                          {/* Address subtext */}
                          <p className="text-[11px] text-cool-gray leading-normal line-clamp-2">
                            <strong>Address:</strong> {address}
                          </p>

                          {/* AI Verdict Box */}
                          <div className="bg-surface-container-lowest border-l-2 border-primary p-3 rounded-r-lg italic shadow-inner">
                            <p className="font-ai-verdict text-ai-verdict text-on-surface-variant leading-relaxed">
                              "{rec.explanation}"
                            </p>
                          </div>
                        </div>

                        {/* Zomato Anchor Link (Always aligned at the bottom) */}
                        <a
                          className="text-primary font-label-caps text-label-caps flex items-center gap-1 hover:underline self-start pt-2 border-t border-gray-100 w-full"
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View on Zomato
                          <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                        </a>

                      </div>
                    </article>
                  );
                })}
              </div>
            )}

            {/* Results metadata summary (Full Width) */}
            {results.meta && (
              <div className="flex flex-wrap justify-between text-xs text-cool-gray p-4 bg-white border border-border-light rounded-xl w-full">
                <div>📊 Candidates Screened: <strong className="text-deep-charcoal">{results.meta.candidates_considered}</strong></div>
                <div>🛠️ Deterministic Filters: <strong className="text-deep-charcoal">{results.meta.filters_applied.join(', ').toUpperCase()}</strong></div>
                <div>⚡ Logic: <strong className="text-deep-charcoal">{results.meta.fallback_used ? 'FALLBACK (Rating)' : 'AI RANKS ACTIVE'}</strong></div>
              </div>
            )}

          </div>
        )}

      </main>

      {/* Brand Footer (Full Width Container) */}
      <footer className="bg-surface-container-low border-t border-border-light mt-12">
        <div className="flex flex-col items-center gap-stack-gap py-section-gap w-full max-w-[1200px] mx-auto px-gutter">
          <div className="font-headline-md text-primary font-extrabold tracking-tighter">Zomato AI</div>
          <p className="font-body-sm text-body-sm text-cool-gray text-center">
            © {new Date().getFullYear()} Zomato AI Advisor. Powered by Zomato Data.
          </p>
          <div className="flex gap-6">
            <a className="font-label-caps text-label-caps text-cool-gray hover:text-primary transition-colors cursor-pointer">Privacy</a>
            <a className="font-label-caps text-label-caps text-cool-gray hover:text-primary transition-colors cursor-pointer">Terms</a>
            <a className="font-label-caps text-label-caps text-cool-gray hover:text-primary transition-colors cursor-pointer">Feedback</a>
          </div>
        </div>
      </footer>

    </div>
  );
}
