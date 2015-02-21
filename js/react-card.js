var Card = React.createClass({
  componentDidMount: function() {
    $(document).foundation();
  },
  render: function() {
    var cx = React.addons.classSet;
    var titleClasses = cx({
      'project-title': true,
      'medium-centered': true,
      'small-centered': true,
      'columns': true,
      'small-6 medium-12': this.props.data.markov,
      'small-5 medium-9': this.props.data.mars,
      'small-4 medium-9': this.props.data.textspiration
    });
    var taglineClasses = cx({
      'tagline': true,
      'medium-centered': true,
      'small-centered': true,
      'columns': true,
      'small-6 medium-11': this.props.data.markov,
      'small-6 medium-11': this.props.data.mars,
      'small-5 medium-9': this.props.data.textspiration
    });
    return(
      <div className="medium-4 columns">
        <header className="small-11 small-centered columns">
          <h3 className={titleClasses}>{this.props.data.title}</h3>
        </header>
        <div className="project-container" data-equalizer-watch>
          <h5 className={taglineClasses}>{this.props.data.subtitle}</h5>
          <div className="screenshot small-8 small-centered columns">
            <a href={this.props.data.link} alt={this.props.data.alt} target="_new"><img src={this.props.data.image} /></a>
          </div>
          <p className="writeup small-10 small-centered columns text-justify">{this.props.data.description}</p>
          <p className="tech small-10 small-centered columns text-justify">{this.props.data.techStack}</p>
          <div className="row">
            <Roles roles={this.props.data.roles} />
            <Links links={this.props.data.links} />
          </div>
        </div>
      </div>
    );
  }
});

var Roles = React.createClass({
  render: function() {
    var allRoles = this.props.roles.map(function(role){
      return (
        <li>{role}</li>
      );
    });
    return (
      <div className="role small-6 columns">
        <ul>
          {allRoles}
        </ul>
      </div>
    );
  }
});

var Links = React.createClass({
  render: function() {
    var projectLinks = this.props.links.map(function(link){
      return (
        <li><a href={link.url} target="_new">{link.text}</a></li>
      );
    });
    return (
      <div className="links small-6 columns">
        <ul>
          {projectLinks}
        </ul>
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
