import Link from "next/link";
import { Video, Users, Film, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Veo Character Consistency
        </h1>
        <p className="text-xl text-muted-foreground">
          Generate stunning videos with perfect character consistency using Veo 3.1
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <Link
          href="/characters"
          className="group p-6 border rounded-lg hover:shadow-lg transition-all hover:border-primary"
        >
          <div className="flex items-center gap-3 mb-3">
            <Users className="w-8 h-8 text-primary" />
            <h2 className="text-2xl font-semibold">Characters</h2>
          </div>
          <p className="text-muted-foreground">
            Create and manage character profiles with face embeddings, outfits, and style locks
          </p>
        </Link>

        <Link
          href="/projects"
          className="group p-6 border rounded-lg hover:shadow-lg transition-all hover:border-primary"
        >
          <div className="flex items-center gap-3 mb-3">
            <Film className="w-8 h-8 text-primary" />
            <h2 className="text-2xl font-semibold">Projects</h2>
          </div>
          <p className="text-muted-foreground">
            Build story timelines with beats and shots. Plan your video sequences
          </p>
        </Link>

        <Link
          href="/generation"
          className="group p-6 border rounded-lg hover:shadow-lg transition-all hover:border-primary"
        >
          <div className="flex items-center gap-3 mb-3">
            <Video className="w-8 h-8 text-primary" />
            <h2 className="text-2xl font-semibold">Generate</h2>
          </div>
          <p className="text-muted-foreground">
            Generate videos with Veo 3.1. Text, image, or video to video
          </p>
        </Link>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-lg p-8">
        <div className="flex items-start gap-4">
          <Sparkles className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-2xl font-semibold mb-3">Key Features</h3>
            <ul className="space-y-2 text-muted-foreground">
              <li>• Character profiles with locked traits and face embeddings (3-10 reference images)</li>
              <li>• Multiple outfit slots: casual, formal, hero, winter</li>
              <li>• Beat-based timeline: hook, conflict, resolution</li>
              <li>• Shot list builder with camera presets: dolly, pan, orbit</li>
              <li>• One-click aspect ratio presets: 9:16, 1:1, 16:9, 4:5</li>
              <li>• Low-res preview and final 4K rendering</li>
              <li>• Continuity validator with similarity scores</li>
              <li>• Style locks to keep hair, skin tone, eyes, and outfit stable</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
