package edu.mit.csail.confer;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.queries.mlt.MoreLikeThis;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

import com.google.gson.Gson;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Reader;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Scanner;

/** 
 * Index papers.json
 * 
 * @author anantb
 * @date 06/13/2013
 * 
 */
public class Indexer {
  String docsPath = "";
  String similarDocsPath = "";
  String indexPath = "";
  boolean create = true;
  
  public Indexer(String docsPath, String similarDocsPath, String indexPath, boolean create) {
    this.docsPath = docsPath;
    this.indexPath = indexPath;
    this.similarDocsPath = similarDocsPath;
    this.create = create;
    
  }

  public static void main(String[] args) { 
    try {
      Indexer indexer = null;
      if(args.length == 3){
        indexer = new Indexer(args[0], args[1], args[2], true);
      }else{
        System.out.println("Required arguments missing");
        System.exit(1);
      }
      indexer.index();
      indexer.getSimilarity();
    } catch (IOException e) {
      System.out.println(
          " caught a " + e.getClass() +
          "\n with message: " + e.getMessage());
    }
  }

  void index() throws IOException{   
    Directory indexDir = FSDirectory.open(new File(this.indexPath));
    Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_40);
    IndexWriterConfig iwc = new IndexWriterConfig(Version.LUCENE_40, analyzer);
    if (create) {
      iwc.setOpenMode(OpenMode.CREATE);
    } else {
      iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);
    }
    IndexWriter writer = new IndexWriter(indexDir, iwc);
   
    StringBuilder text = new StringBuilder();
    Scanner scanner = new Scanner(new FileInputStream(this.docsPath));
    try {
      while (scanner.hasNextLine()){
        text.append(scanner.nextLine());
      }
    } catch (Exception e){
      
    }

    scanner.close();    
    //System.out.println(text);
    Map<String, Map<String, Object>> papers = new HashMap<String,Map<String, Object>>();
    Gson gson = new Gson();
    papers=(Map<String,Map<String,Object>>)gson.fromJson(text.toString(), papers.getClass());
    Iterator<String> iterator = papers.keySet().iterator();
    while (iterator.hasNext()) {  
      String paper_id = iterator.next().toString();  
      Map<String, Object> paper_details = papers.get(paper_id);
      String title = paper_details.get("title").toString();
      String abstrct = paper_details.get("abstract").toString();
      //System.out.println(title);
      //System.out.println(abstrct);
      //System.out.println(session);
      //System.out.println(title);
      Document doc = new Document();   
      Field f_paper_id = new Field("paper_id", paper_id, Field.Store.YES, Field.Index.NOT_ANALYZED);
      Field f_title = new Field("title", title, Field.Store.YES, Field.Index.ANALYZED);
      Field f_abstract = new Field("abstract", abstrct, Field.Store.YES, Field.Index.ANALYZED);
      f_title.setBoost((float) 10.0);
      f_abstract.setBoost((float) 1.0);
      doc.add(f_paper_id);
      doc.add(f_title);
      doc.add(f_abstract);

      if (writer.getConfig().getOpenMode() == OpenMode.CREATE) {
        writer.addDocument(doc);
      } else {
        writer.updateDocument(new Term("docId", paper_id), doc);
      }

    }  
    writer.close();   
  }
  
  void getSimilarity() throws IOException {      
    IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(this.indexPath)));
    IndexSearcher searcher = new IndexSearcher(reader);
    Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_40);
    MoreLikeThis mlt = new MoreLikeThis(reader); // Pass the index reader
    mlt.setAnalyzer(analyzer);
    mlt.setFieldNames(null); // specify the fields for similiarity
    HashMap<String, ArrayList<HashMap<String, Float>>> similar_docs = new HashMap<String, ArrayList<HashMap<String,Float>>>();
    for (int i=0; i<reader.maxDoc(); i++) { 
      ArrayList<HashMap<String, Float>> t = new ArrayList<HashMap<String,Float>>();
      Query query = mlt.like(i);
      TopDocs similarDocs = searcher.search(query, 20); // Use the searcher
      ScoreDoc[] docs = similarDocs.scoreDocs;
      mlt.setMaxQueryTerms(1000);
      mlt.setMinTermFreq(1);
      mlt.setMinDocFreq(1);
      for(int k=0; k<docs.length; k++){
        if(docs[k].doc == i)
          continue;
        HashMap<String, Float> m = new HashMap<String, Float>();
        m.put(reader.document(docs[k].doc).getField("paper_id").stringValue(), docs[k].score);
        t.add(m);
      }

      similar_docs.put(reader.document(i).getField("paper_id").stringValue(), t);
    }

    Gson gson = new Gson(); 
    String json = gson.toJson(similar_docs); 
    PrintWriter out = new PrintWriter(this.similarDocsPath);
    out.println("offline_recs=" + json);
    out.close();
  } 

}
