var Card = React.createClass({
  render: function() {
    return(
      <div className="medium-4 columns">
        <header className="small-11 small-centered columns">
          <h3 className="project-title small-6 medium-12 small-centered medium-centered columns">{this.props.data.title}</h3>
        </header>
        <div className="project-container" data-equalizer-watch>
          <h5 className="tagline small-6 medium-11 small-centered medium-centered columns">{this.props.data.subtitle}</h5>
          <div className="screenshot small-8 small-centered columns">
            <a href={this.props.data.link} alt={this.props.data.alt} target="_new"><img src={this.props.data.image} /></a>
          </div>
          <p className="writeup small-10 small-centered columns text-justify">{this.props.data.description}</p>
          <p className="tech small-10 small-centered columns text-justify">{this.props.data.techStack}</p>
          <div className="row">
            <div className="role small-6 columns">
              <ul>
                <li>developer</li>
                <li>designer</li>
              </ul>
            </div>
            <div className="links small-6 columns">
              <ul>
                <li><a href="https://markovqaurelius.herokuapp.com/" target="_new">live project</a></li>
                <li><a href="https://github.com/chrisbodhi/stoic_generator" target="_new">source code</a></li>
                <li><a href="https://twitter.com/markovQaurelius" target="_new">on twitter</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }
});

var Dealer = React.createClass({
  loadCardInfoFromServer: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: []};
  },
  render: function() {
    return (
      this.loadCardInfoFromServer(),
      <Deck data={this.state.data} />
    );
  }
});

var Deck = React.createClass({
  render: function() {
    var cardList = this.props.data.map(function (card) {
      return (
        <Card data={card} />
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
  <Dealer url="js/data.json" />,
  document.getElementById('content')
);