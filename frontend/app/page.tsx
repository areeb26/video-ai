import Link from "next/link";
import { Video, Users, Film, Sparkles, Zap, Target } from "lucide-react";

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16 pt-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-medium mb-6">
          <Zap className="w-4 h-4" />
          Powered by Veo 3.1
        </div>
        <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-cyan-500 via-teal-500 to-emerald-500 bg-clip-text text-transparent">
          Veo Character Consistency
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
          Create stunning videos with perfect character consistency. Professional AI video generation with advanced face embeddings and style locks.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/characters">
            <button className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-all shadow-lg hover:shadow-xl">
              Get Started
            </button>
          </Link>
          <Link href="/generation">
            <button className="px-6 py-3 border-2 border-primary text-primary rounded-lg font-semibold hover:bg-primary/5 transition-all">
              Try Demo
            </button>
          </Link>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
        <Link
          href="/characters"
          className="group relative p-8 border-2 rounded-2xl hover:shadow-2xl transition-all hover:border-primary overflow-hidden bg-gradient-to-br from-white to-cyan-50/30 dark:from-gray-900 dark:to-cyan-950/20"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-16 -mt-16" />
          <div className="relative">
            <div className="w-14 h-14 bg-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Users className="w-7 h-7 text-primary" />
            </div>
            <h2 className="text-2xl font-bold mb-3">Characters</h2>
            <p className="text-muted-foreground leading-relaxed">
              Create detailed character profiles with face embeddings, multiple outfits, and advanced style locks
            </p>
          </div>
        </Link>

        <Link
          href="/projects"
          className="group relative p-8 border-2 rounded-2xl hover:shadow-2xl transition-all hover:border-primary overflow-hidden bg-gradient-to-br from-white to-teal-50/30 dark:from-gray-900 dark:to-teal-950/20"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-16 -mt-16" />
          <div className="relative">
            <div className="w-14 h-14 bg-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Film className="w-7 h-7 text-primary" />
            </div>
            <h2 className="text-2xl font-bold mb-3">Projects</h2>
            <p className="text-muted-foreground leading-relaxed">
              Build story timelines with beats and shots. Professional video planning tools
            </p>
          </div>
        </Link>

        <Link
          href="/generation"
          className="group relative p-8 border-2 rounded-2xl hover:shadow-2xl transition-all hover:border-primary overflow-hidden bg-gradient-to-br from-white to-emerald-50/30 dark:from-gray-900 dark:to-emerald-950/20"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-16 -mt-16" />
          <div className="relative">
            <div className="w-14 h-14 bg-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Video className="w-7 h-7 text-primary" />
            </div>
            <h2 className="text-2xl font-bold mb-3">Generate</h2>
            <p className="text-muted-foreground leading-relaxed">
              Text-to-video, image-to-video, and video-to-video generation with Veo 3.1
            </p>
          </div>
        </Link>
      </div>

      {/* Features Section */}
      <div className="bg-gradient-to-r from-cyan-50 via-teal-50 to-emerald-50 dark:from-cyan-950/20 dark:via-teal-950/20 dark:to-emerald-950/20 rounded-2xl p-10 border-2 border-primary/20 mb-16">
        <div className="flex items-start gap-6">
          <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-8 h-8 text-primary" />
          </div>
          <div>
            <h3 className="text-3xl font-bold mb-6">Powerful Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <Target className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold mb-1">Face Embeddings</p>
                  <p className="text-sm text-muted-foreground">3-10 reference images for perfect character consistency</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Target className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold mb-1">Multiple Outfits</p>
                  <p className="text-sm text-muted-foreground">Casual, formal, hero, winter outfit slots</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Target className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold mb-1">Beat-Based Timeline</p>
                  <p className="text-sm text-muted-foreground">Hook, conflict, resolution story structure</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Target className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold mb-1">Camera Presets</p>
                  <p className="text-sm text-muted-foreground">Dolly, pan, orbit, tilt, zoom movements</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Target className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold mb-1">Aspect Ratios</p>
                  <p className="text-sm text-muted-foreground">9:16, 1:1, 16:9, 4:5 one-click presets</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Target className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold mb-1">4K Rendering</p>
                  <p className="text-sm text-muted-foreground">Low-res preview and final 4K quality</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Target className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold mb-1">Continuity Validator</p>
                  <p className="text-sm text-muted-foreground">AI-powered similarity scores and drift detection</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Target className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold mb-1">Style Locks</p>
                  <p className="text-sm text-muted-foreground">Lock hair, skin tone, eyes, and outfit</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
