// @license magnet:?xt=urn:btih:1f739d935676111cfff4b4693e3816e664797050&dn=gpl-3.0.txt GPL-v3
// Copyright (C) 2022 Eklavya Sharma. Licensed under GNU GPLv3.
'use strict';

var articles = null;

function filterArticles(condition) {
    if(articles !== null) {
        for(const [id, article] of Object.entries(articles)) {
            var elem = document.getElementById('article.' + id);
            if(condition(article)) {
                elem.classList.remove("hidden");
            }
            else {
                elem.classList.add("hidden");
            }
        }
    }
}

function hasTopicF(topic) {
    return function(article) {
        return article.hasOwnProperty('topics') && article.topics.hasOwnProperty(topic);
    }
}

function hasSubtopicF(topic, subtopic) {
    return function(article) {
        return hasTopicF(article) && article.topics[topic].includes(subtopic);
    }
}

function andF(conditions) {
    return function(article) {
        for(const condition of conditions) {
            if(! condition(article)) {
                return false;
            }
        }
        return true;
    }
}

function orF(conditions) {
    return function(article) {
        for(const condition of conditions) {
            if(condition(article)) {
                return true;
            }
        }
        return false;
    }
}

function main() {
    window.fetch('articles.json')
        .then(function(response) {return response.json();})
        .then(function(data) {articles = data;});
}

window.addEventListener('load', main);

// @license-end
