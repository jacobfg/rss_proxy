package main

import (
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
	"golang.org/x/net/html"
)

func main() {
	r := gin.Default()

	r.GET("/koala_sleep", koalaSleep)
	r.GET("/the_grow_your_mind", theGrowYourMind)

	r.Run(":8888")
}

func koalaSleep(c *gin.Context) {
	targetURL := "https://feeds.megaphone.fm/NSR5390218838"
	response, err := fetchRSS(targetURL)
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to fetch RSS feed")
		return
	}

	filteredXML, err := processXML(response)
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to process RSS feed")
		return
	}

	c.Data(http.StatusOK, "application/xml", []byte(filteredXML))
}

func theGrowYourMind(c *gin.Context) {
	targetURL := "https://omny.fm/shows/the-grow-your-mind-podcast/playlists/podcast.rss"
	response, err := fetchRSS(targetURL)
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to fetch RSS feed")
		return
	}

	filteredXML, err := processXML(response)
	if err != nil {
		c.String(http.StatusInternalServerError, "Failed to process RSS feed")
		return
	}

	c.Data(http.StatusOK, "application/xml", []byte(filteredXML))
}

func fetchRSS(url string) (string, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", err
	}
	req.Header.Add("Content-Type", "text/xml")
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("Failed to fetch RSS feed. Status code: %d", resp.StatusCode)
	}

	buf := &strings.Builder{}
	_, err = io.Copy(buf, resp.Body)
	if err != nil {
		return "", err
	}

	return buf.String(), nil
}

func processXML(xmlData string) (string, error) {
	doc, err := html.Parse(strings.NewReader(xmlData))
	if err != nil {
		return "", err
	}

	// Define a regex pattern to match unwanted episode titles
	regexPattern := `(^Teachers!|S\d+\s-\sS[oO][nN][gG]\s\d+\s-\s)`
	re := regexp.MustCompile(regexPattern)

	var nodesToRemove []*html.Node

	var filter func(*html.Node)
	filter = func(n *html.Node) {
		if n.Type == html.ElementNode {
			if n.Data == "title" {
				if re.MatchString(n.FirstChild.Data) {
					// Find the parent node of the title and add it to nodesToRemove
					if n.Parent != nil {
						nodesToRemove = append(nodesToRemove, n.Parent)
					}
					return
				}
			} else if n.Data == "enclosure" {
				linkFromEnclosure(n)
			}
		}

		for c := n.FirstChild; c != nil; c = c.NextSibling {
			filter(c)
		}
	}

	filter(doc)

	var filter2 func(*html.Node)
	filter2 = func(n *html.Node) {
		var nodesToRemove []*html.Node

		var dfs func(n *html.Node)
		dfs = func(n *html.Node) {
			if n.Type == html.ElementNode {
				if n.Data != "link" && n.Data != "episode" && n.Data != "season" && n.Data != "title" {
					nodesToRemove = append(nodesToRemove, n)
					return
				}
			}

			for c := n.FirstChild; c != nil; c = c.NextSibling {
				dfs(c)
			}
		}

		dfs(n)

		// Remove nodes that need to be removed
		for _, node := range nodesToRemove {
			parent := node.Parent
			if parent != nil {
				parent.RemoveChild(node)
			}
		}
	}

	filter2(doc)

	// Remove nodes that need to be removed
	for _, node := range nodesToRemove {
		parent := node.Parent
		if parent != nil {
			parent.RemoveChild(node)
		}
	}

	var result strings.Builder
	err = html.Render(&result, doc)
	if err != nil {
		return "", err
	}

	return result.String(), nil
}

func linkFromEnclosure(enclosureNode *html.Node) {
	link := &html.Node{
		Type: html.ElementNode,
		Data: "link",
	}
	for _, attr := range enclosureNode.Attr {
		if attr.Key == "url" {
			link.Attr = append(link.Attr, html.Attribute{
				Key: "href",
				Val: strings.Split(attr.Val, "?")[0],
			})
			break
		}
	}
	if enclosureNode.Parent != nil {
		enclosureNode.Parent.InsertBefore(link, enclosureNode)
	}
}
