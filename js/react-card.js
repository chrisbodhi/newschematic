var data = [
{"title": "Markov Q. Aurelius","subtitle": "A Philosopher for the 21st Century"},
{"title": "Mars Attracts!","subtitle": "Book a Flight to Mars! (Not Really)"},
{"title": "Textspiration","subtitle": "Inspirational Messages to your Phone Daily"}
]

var Card = React.createClass({
  render: function() {
    return(
      <div className="medium-4 columns">
        <header className="small-11 small-centered columns">
          <h3 className="project-title small-6 medium-12 small-centered medium-centered columns">{this.props.title}</h3>
        </header>
        <div className="project-container" data-equalizer-watch>
          <h5 className="tagline small-6 medium-11 small-centered medium-centered columns">{this.props.subtitle}</h5>
        </div>
      </div>
    );
  }
});

var Deck = React.createClass({
  render: function() {
    var cardList = this.props.data.map(function (card) {
      return (
        <Card title={card.title} subtitle={card.subtitle} />
      );
    });
    return (
      <div className="deck">
        {cardList}
      </div>
    );
  }
});

React.render(
  <Deck data={data} />,
  document.getElementById('content')
);