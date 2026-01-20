package models

type WhisperResult struct {
	Language string    `json:"language"`
	Duration           float64   `json:"duration"`
	ProcessingDuration float64   `json:"processing_duration"`
	Segments           []Segment `json:"segments"`
	Text     string    `json:"text"`
}

type Segment struct {
	End     float64 `bson:"end" json:"end"`
	ID      string  `bson:"id" json:"id"`
	Start   float64 `bson:"start" json:"start"`
	Score   float64 `bson:"score" json:"score"`
	Text    string  `bson:"text" json:"text"`
	Speaker string  `bson:"speaker" json:"speaker"`
	Role    string  `bson:"role" json:"role"`
	Words   []Word  `bson:"words" json:"words"`
}

type Word struct {
	End   float64 `json:"end"`
	Start float64 `json:"start"`
	Word  string  `json:"word"`
	Score float64 `json:"score"`
}
