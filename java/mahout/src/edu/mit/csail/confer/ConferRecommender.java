package edu.mit.csail.confer;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.recommender.GenericBooleanPrefItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.LogLikelihoodSimilarity;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;

import py4j.GatewayServer;
// Discussion about algorithm for recommendation

public class ConferRecommender {
  ItemBasedRecommender recommender;
  
  public ConferRecommender(int conference_id) throws RecommenderBuildException {
    FileDataModel dataModel = new FileDataModel(new File("D://input.txt"));
    ItemSimilarity itemSimilarity = new LogLikelihoodSimilarity(dataModel);
    recommender =new GenericBooleanPrefItemBasedRecommender(dataModel, itemSimilarity);
  }
  
  public ArrayList<String> recommend(ArrayList<String> i_items){
    Set<Long> input_items = new HashSet<Long>();
    for (String i : i_items){ 
      input_items.add(Long.valueOf(i)); 
    }

    ArrayList<String> ret = new ArrayList<String>();
    List<RecommendedItem> recommendations = this.recommender.mostSimilarItems(input_items, 20);
    int len = recommendations.size();

    for(int i=0; i< len; i++){
      ret.add(recommendations[i].getItemId() + "," + recommendations[i].getValue());
    }
    return ret;
  }
  
  public static void main(String[] args){   
    try{
      ConferRecommender r = new ConferRecommender(args[0]);
      GatewayServer gatewayServer = new GatewayServer(r);
      gatewayServer.start();
      System.out.println("Gateway Server Started");
    }catch(RecommenderBuildException rbe){
      rbe.printStackTrace();
    }   
    
    
  }

}
