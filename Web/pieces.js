/* Star Song: the pieces in the collection.
   Wandering Stars is free. Every other piece is unlocked by one purchase, the Star Song bundle,
   whose product ID must match bundleProductId below in App Store Connect and in Google Play Console.
   To add a piece later, put it in Web/pieces/<id>/ (index.html + thumb.jpg) and add it to the list. */
window.COLLECTION = {
  title: 'Star Song',
  subtitle: 'Night-sky pieces that play themselves',
  bundleProductId: 'starsong.bundle',
  bundleName: 'The Star Song collection',
  /* Paste your store links here once the apps are live; the website shows them as buttons. */
  appStoreUrl: '',
  playStoreUrl: ''
};
window.PIECES = [
  { id: 'wandering-stars', title: 'Wandering Stars', free: true,
    blurb: 'Comets fall around a sun and play chords as they cross the rings of a gilded star chart.' },
  { id: 'constellations', title: 'Constellations',
    blurb: 'Every star is a note. Each chord draws its own constellation, slips away, and returns.' },
  { id: 'nursery-of-stars', title: 'The Nursery of Stars',
    blurb: 'An antique star chart drawn one note at a time; each resting chord names a new constellation.' },
  { id: 'star-trails', title: 'Star Trails',
    blurb: 'A long exposure of the night sky. Each voice is a star wheeling round the pole.' },
  { id: 'the-orrery', title: 'The Orrery',
    blurb: 'Planets loop around three suns on a Victorian plate, sounding bells as they cross their orbits.' },
  { id: 'ground-tracks', title: 'Ground Tracks',
    blurb: 'Each voice is a satellite; the chord is the braid of their tracks over the Earth.' },
  { id: 'deep-field-receiver', title: 'Deep Field Receiver',
    blurb: 'A radio telescope listening to deep space: every voice a signal line in the waterfall.' },
  { id: 'cymatics', title: 'Cymatics',
    blurb: 'Sand on a singing plate. Every held chord shakes the sand into its own figure.' }
];
