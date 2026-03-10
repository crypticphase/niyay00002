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

export interface Item {
  id: string;
  name: string;
  type: string;
  description: string;
  ability: string;
}

export interface PlotPoint {
  id: string;
  title: string;
  description: string;
  act: '1' | '2' | '3';
}

export interface Chapter {
  id: string;
  title: string;
  content: string;
}

export interface StoryState {
  id: string;
  title: string;
  synopsis: string;
  genre: string;
  characters: Character[];
  worldSettings: WorldSetting[];
  items: Item[];
  plotPoints: PlotPoint[];
  chapters: Chapter[];
  currentChapterId: string;
  messages: ChatMessage[];
}

export interface ChatMessage {
  role: 'user' | 'model';
  content: string;
}
