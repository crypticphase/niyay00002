export interface Character {
  id: string;
  name: string;
  role: string;
  description: string;
  traits: string[];
  goals: string;
}

export interface WorldSetting {
  id: string;
  title: string;
  description: string;
  rules: string;
}

export interface StoryState {
  title: string;
  synopsis: string;
  characters: Character[];
  worldSettings: WorldSetting[];
  manuscript: string;
}

export interface ChatMessage {
  role: 'user' | 'model';
  content: string;
}
