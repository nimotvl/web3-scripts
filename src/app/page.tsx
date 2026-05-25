export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Web3 Scripts</h1>
        
        <div className="grid gap-6">
          <section className="bg-gray-900 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">K25.ai Registration</h2>
            <p className="text-gray-400 mb-4">
              Automated registration script for K25.ai platform with email verification.
            </p>
            <code className="text-green-400">k25ai_register.py</code>
          </section>

          <section className="bg-gray-900 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Paper Trading</h2>
            <p className="text-gray-400 mb-4">
              Paper trading engine for testing Web3 trading strategies without real funds.
            </p>
            <code className="text-green-400">paper_trade.py</code>
          </section>

          <section className="bg-gray-900 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Webshare Registration</h2>
            <p className="text-gray-400 mb-4">
              Automated proxy registration with Webshare for multi-account operations.
            </p>
            <code className="text-green-400">webshare_register.py</code>
          </section>
        </div>

        <footer className="mt-12 text-gray-500 text-sm">
          Built with Next.js • Web3 Automation Tools
        </footer>
      </div>
    </main>
  );
}
